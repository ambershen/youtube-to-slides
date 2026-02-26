"""Main pipeline orchestrator for YouTube-to-Slides."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from yt_slides.ai.gemini_client import create_client
from yt_slides.ai.prompt_builder import build_infographic_prompt
from yt_slides.ai.segmenter import consolidate_sections, segment_transcript
from yt_slides.ai.summarizer import summarize_section
from yt_slides.config import Settings
from yt_slides.image.generator import generate_infographic
from yt_slides.models import InfographicResult, Section
from yt_slides.youtube.chapters import (
    assign_transcript_to_sections,
    parse_chapters_from_description,
    split_by_time,
)
from yt_slides.youtube.metadata import fetch_metadata
from yt_slides.youtube.transcript import fetch_transcript
from yt_slides.youtube.url_parser import extract_video_id


def _slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:50]


def run_pipeline(
    url: str,
    settings: Settings,
    style: str = "modern",
    dry_run: bool = False,
    console: Console | None = None,
) -> list[InfographicResult]:
    """Run the full YouTube-to-Slides pipeline."""
    console = console or Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        client = None

        # Step 1: Parse URL
        task = progress.add_task("[cyan]Parsing YouTube URL...", total=None)
        video_id = extract_video_id(url)
        console.print(f"  Video ID: [bold]{video_id}[/bold]")
        progress.remove_task(task)

        # Step 2: Fetch metadata
        task = progress.add_task("[cyan]Fetching video metadata...", total=None)
        metadata = fetch_metadata(video_id)
        console.print(f"  Title: [bold]{metadata.title}[/bold]")
        console.print(f"  Duration: {metadata.duration_seconds // 60}m {metadata.duration_seconds % 60}s")
        progress.remove_task(task)

        # Step 3: Fetch transcript
        task = progress.add_task("[cyan]Fetching transcript...", total=None)
        transcript = fetch_transcript(video_id)
        console.print(f"  Transcript: {len(transcript)} snippets")
        progress.remove_task(task)

        # Step 4: Detect sections
        task = progress.add_task("[cyan]Detecting sections...", total=None)
        sections = _detect_sections(
            metadata, transcript, settings, console
        )
        if settings.max_sections > 0 and len(sections) > settings.max_sections:
            console.print(f"  [yellow]Consolidating {len(sections)} sections into {settings.max_sections} slides...[/yellow]")
            client = create_client(settings.gemini_api_key)
            sections = _call_with_rate_limit(
                lambda: consolidate_sections(
                    client=client,
                    sections=sections,
                    target_count=settings.max_sections,
                    video_title=metadata.title,
                    model=settings.gemini_text_model,
                ),
                console=console,
            )
        console.print(f"  Sections: {len(sections)}")
        for s in sections:
            m, sec = divmod(int(s.start_seconds), 60)
            console.print(f"    [{m}:{sec:02d}] {s.title}")
        progress.remove_task(task)

        # Step 5: Summarize sections
        task = progress.add_task("[cyan]Summarizing sections...", total=None)
        if not client:
            client = create_client(settings.gemini_api_key)
        summaries = []
        for i, section in enumerate(sections):
            summary = _call_with_rate_limit(
                lambda s=section: summarize_section(
                    client=client,
                    section=s,
                    video_title=metadata.title,
                    total_sections=len(sections),
                    max_words=settings.max_words_per_infographic,
                    model=settings.gemini_text_model,
                ),
                console=console,
            )
            summaries.append(summary)
            console.print(f"    [dim]Summarized ({i+1}/{len(sections)}): {section.title}[/dim]")
            # Pace requests to stay within free-tier rate limits
            if i < len(sections) - 1:
                time.sleep(13)
        progress.remove_task(task)

        # Step 6: Build prompts
        task = progress.add_task("[cyan]Building infographic prompts...", total=None)
        prompts: list[str] = []
        for summary in summaries:
            prompt = build_infographic_prompt(
                summary=summary,
                video_title=metadata.title,
                total_sections=len(sections),
                style=style,
            )
            prompts.append(prompt)
        progress.remove_task(task)

        # Step 7: Generate images (or dry-run)
        output_dir = Path(settings.output_dir) / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[InfographicResult] = []

        if dry_run:
            task = progress.add_task("[yellow]Dry run — printing prompts...", total=None)
            for i, (section, prompt) in enumerate(zip(sections, prompts)):
                console.print(f"\n[bold]--- Slide {i + 1}: {section.title} ---[/bold]")
                console.print(prompt)
                results.append(
                    InfographicResult(
                        section_index=section.index,
                        section_title=section.title,
                        image_path=str(output_dir / f"{i + 1:02d}_{_slugify(section.title)}.{settings.image_format}"),
                        prompt_used=prompt,
                    )
                )
            progress.remove_task(task)
        else:
            task = progress.add_task("[cyan]Generating infographics...", total=None)
            for i, (section, prompt) in enumerate(zip(sections, prompts)):
                filename = f"{i + 1:02d}_{_slugify(section.title)}.{settings.image_format}"
                output_path = output_dir / filename
                console.print(f"  Generating slide {i + 1}/{len(sections)}: {section.title}")
                _call_with_rate_limit(
                    lambda p=prompt, o=output_path: generate_infographic(
                        client=client,
                        prompt=p,
                        output_path=o,
                        model=settings.gemini_image_model,
                        aspect_ratio=settings.image_aspect_ratio,
                    ),
                    console=console,
                )
                results.append(
                    InfographicResult(
                        section_index=section.index,
                        section_title=section.title,
                        image_path=str(output_path),
                        prompt_used=prompt,
                    )
                )
                # Pace requests for rate limits
                if i < len(sections) - 1:
                    time.sleep(13)
            progress.remove_task(task)

        # Step 8: Save metadata
        meta_path = output_dir / "metadata.json"
        meta_path.write_text(
            json.dumps(
                {
                    "video_id": video_id,
                    "video_title": metadata.title,
                    "video_url": url,
                    "channel": metadata.channel_title,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "style": style,
                    "sections": [
                        {
                            "index": r.section_index,
                            "title": r.section_title,
                            "image_file": Path(r.image_path).name,
                        }
                        for r in results
                    ],
                },
                indent=2,
            )
        )
        console.print(f"\n  Metadata saved to {meta_path}")

    return results


def _call_with_rate_limit(func, console: Console, max_retries: int = 3):
    """Call a function with automatic retry on rate limit (429) errors."""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries:
                    # Extract retry delay from error if available
                    wait = 60
                    import re as _re
                    delay_match = _re.search(r"retry in (\d+)", error_str, _re.IGNORECASE)
                    if delay_match:
                        wait = int(delay_match.group(1)) + 5
                    console.print(f"    [yellow]Rate limited. Waiting {wait}s...[/yellow]")
                    time.sleep(wait)
                    continue
            raise


def _detect_sections(
    metadata, transcript, settings: Settings, console: Console
) -> list[Section]:
    """Detect sections via chapters, AI segmentation, or time-based fallback."""
    # Try parsing chapters from description
    chapters = parse_chapters_from_description(
        metadata.description, metadata.duration_seconds
    )
    if chapters:
        console.print("  [green]Found chapters in video description[/green]")
        return assign_transcript_to_sections(chapters, transcript)

    # Try AI segmentation
    console.print("  [yellow]No chapters found — using AI segmentation...[/yellow]")
    try:
        client = create_client(settings.gemini_api_key)
        return segment_transcript(
            client=client,
            transcript=transcript,
            metadata=metadata,
            model=settings.gemini_text_model,
        )
    except Exception as e:
        console.print(f"  [red]AI segmentation failed: {e}[/red]")
        console.print("  [yellow]Falling back to time-based splitting...[/yellow]")
        return split_by_time(transcript, metadata.duration_seconds)

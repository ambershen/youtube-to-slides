"""AI-powered transcript segmentation when no chapters exist."""

import json

from google import genai
from google.genai import types

from yt_slides.models import Section, TranscriptSnippet, VideoMetadata


def _format_transcript_with_timestamps(
    transcript: list[TranscriptSnippet],
) -> str:
    """Format transcript with periodic timestamps for the LLM."""
    lines: list[str] = []
    last_ts = -30.0
    for snippet in transcript:
        if snippet.start - last_ts >= 15:
            minutes = int(snippet.start // 60)
            seconds = int(snippet.start % 60)
            lines.append(f"\n[{minutes}:{seconds:02d}] ")
            last_ts = snippet.start
        lines.append(snippet.text)
    return "".join(lines)


def segment_transcript(
    client: genai.Client,
    transcript: list[TranscriptSnippet],
    metadata: VideoMetadata,
    model: str = "gemini-2.5-flash",
) -> list[Section]:
    """Use Gemini to identify logical sections in the transcript."""
    duration_min = metadata.duration_seconds / 60
    formatted = _format_transcript_with_timestamps(transcript)

    prompt = f"""You are analyzing a YouTube video transcript to identify logical sections.

Video title: {metadata.title}
Video duration: {duration_min:.1f} minutes

Below is the transcript with timestamps. Identify 4-10 logical sections based on
topic changes, transitions, or natural breaking points.

For each section, provide:
- title: A concise descriptive title (3-8 words)
- start_seconds: The timestamp (in seconds) where this section begins
- end_seconds: The timestamp (in seconds) where this section ends

Rules:
- Sections must be contiguous (no gaps, no overlaps)
- First section starts at 0, last section ends at {metadata.duration_seconds}
- Each section should be 1-10 minutes long
- Prefer natural topic transitions as boundaries

Return a JSON object with a "sections" array. Example:
{{"sections": [{{"title": "Introduction", "start_seconds": 0, "end_seconds": 120}}, ...]}}

Transcript:
{formatted}"""

    response = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    data = json.loads(response.text)
    sections: list[Section] = []

    for i, s in enumerate(data["sections"]):
        section_text = " ".join(
            t.text
            for t in transcript
            if s["start_seconds"] <= t.start < s["end_seconds"]
        )
        sections.append(
            Section(
                index=i + 1,
                title=s["title"],
                start_seconds=s["start_seconds"],
                end_seconds=s["end_seconds"],
                transcript_text=section_text,
            )
        )

    return sections


def consolidate_sections(
    client: genai.Client,
    sections: list[Section],
    target_count: int,
    video_title: str,
    model: str = "gemini-2.5-flash",
) -> list[Section]:
    """Merge many sections into fewer consolidated slides using AI.

    Groups related sections together and produces new titles that span
    the merged content.
    """
    if len(sections) <= target_count:
        return sections

    sections_desc = "\n".join(
        f"  {s.index}. [{int(s.start_seconds//60)}:{int(s.start_seconds%60):02d}] "
        f"{s.title} ({int((s.end_seconds - s.start_seconds)//60)}m)"
        for s in sections
    )

    prompt = f"""You are re-packaging a {len(sections)}-section YouTube video into exactly {target_count} slides.

Video: {video_title}

Current sections:
{sections_desc}

Group these {len(sections)} sections into exactly {target_count} consolidated slides. Each slide should:
- Combine 1-4 related sections into a single coherent theme
- Have a new, compelling title that captures the combined content
- Cover the video from start to finish (no sections left out)

Return a JSON object with a "groups" array. Each group has:
- title: New slide title (3-8 words, compelling and descriptive)
- section_indices: Array of original section indices (1-based) to merge

Example: {{"groups": [{{"title": "Introduction & Background", "section_indices": [1, 2]}}, ...]}}

Rules:
- Exactly {target_count} groups
- Every section index from 1 to {len(sections)} must appear exactly once
- Keep indices in order within each group
- Group thematically related sections together"""

    response = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    data = json.loads(response.text)
    section_map = {s.index: s for s in sections}
    consolidated: list[Section] = []

    for i, group in enumerate(data["groups"]):
        indices = group["section_indices"]
        merged = [section_map[idx] for idx in indices]
        consolidated.append(
            Section(
                index=i + 1,
                title=group["title"],
                start_seconds=merged[0].start_seconds,
                end_seconds=merged[-1].end_seconds,
                transcript_text=" ".join(s.transcript_text for s in merged),
            )
        )

    return consolidated

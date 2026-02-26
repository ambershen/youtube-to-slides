"""CLI entry point for yt-slides."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from yt_slides.config import Settings
from yt_slides.pipeline import run_pipeline

app = typer.Typer(name="yt-slides", help="Convert YouTube videos into infographic slides")
console = Console()


@app.command()
def generate(
    url: str = typer.Argument(..., help="YouTube video URL"),
    output_dir: Path = typer.Option(Path("./output"), "--output", "-o", help="Output directory"),
    aspect_ratio: str = typer.Option("16:9", "--ar", help="Aspect ratio (16:9, 4:3, 1:1)"),
    style: str = typer.Option("davinci", "--style", help="Style: davinci, magazine, comic, geek, chalkboard, collage, newspaper"),
    max_sections: int = typer.Option(0, "--max-sections", help="Max sections (0=unlimited)"),
    gemini_key: str = typer.Option(None, "--gemini-key", envvar="GEMINI_API_KEY"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show prompts without generating images"),
) -> None:
    """Generate infographic slides from a YouTube video."""
    # Load from .env first, then override with CLI flags if provided
    overrides: dict = {
        "output_dir": output_dir,
        "image_aspect_ratio": aspect_ratio,
        "max_sections": max_sections,
    }
    if gemini_key:
        overrides["gemini_api_key"] = gemini_key
    settings = Settings(**overrides)

    if not settings.gemini_api_key:
        console.print("[red]Error: GEMINI_API_KEY is required. Set via --gemini-key or .env file.[/red]")
        raise typer.Exit(1)

    results = run_pipeline(
        url=url,
        settings=settings,
        style=style,
        dry_run=dry_run,
        console=console,
    )

    console.print()
    if dry_run:
        console.print(f"[green]Dry run complete. Generated {len(results)} prompts.[/green]")
    else:
        console.print(f"[green]Done! Generated {len(results)} infographic slides.[/green]")
        console.print(f"[dim]Output: {results[0].image_path.rsplit('/', 1)[0]}[/dim]")


if __name__ == "__main__":
    app()

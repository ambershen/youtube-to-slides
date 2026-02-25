"""Parse chapter markers from YouTube video descriptions."""

from __future__ import annotations

import re

from yt_slides.models import Chapter, Section, TranscriptSnippet


def _timestamp_to_seconds(ts: str) -> float:
    """Convert '1:23:45' or '23:45' to seconds."""
    parts = ts.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0.0


def parse_chapters_from_description(
    description: str, video_duration_seconds: int
) -> list[Chapter] | None:
    """Extract chapters from a video description.

    Returns None if no valid chapter list is found.
    Chapters require: starts near 0:00, at least 3 entries.
    """
    # Match patterns like "0:00 Introduction" or "0:00 - Introduction" or "(0:00) Introduction"
    pattern = r"^\s*\(?(\d{1,2}:\d{2}(?::\d{2})?)\)?\s*[-–—:]?\s*(.+)$"
    matches = re.findall(pattern, description, re.MULTILINE)

    if len(matches) < 3:
        return None

    raw = [(m[1].strip(), _timestamp_to_seconds(m[0])) for m in matches]

    # First chapter must start at or very near 0:00
    if raw[0][1] > 5:
        return None

    chapters: list[Chapter] = []
    for i, (title, start) in enumerate(raw):
        end = raw[i + 1][1] if i + 1 < len(raw) else float(video_duration_seconds)
        chapters.append(Chapter(title=title, start_seconds=start, end_seconds=end))

    return chapters


def assign_transcript_to_sections(
    chapters: list[Chapter],
    transcript: list[TranscriptSnippet],
) -> list[Section]:
    """Map transcript snippets into chapter-defined sections."""
    sections: list[Section] = []
    for i, chapter in enumerate(chapters):
        section_text = " ".join(
            s.text
            for s in transcript
            if chapter.start_seconds <= s.start < chapter.end_seconds
        )
        sections.append(
            Section(
                index=i + 1,
                title=chapter.title,
                start_seconds=chapter.start_seconds,
                end_seconds=chapter.end_seconds,
                transcript_text=section_text,
            )
        )
    return sections


def split_by_time(
    transcript: list[TranscriptSnippet],
    video_duration_seconds: int,
    interval_seconds: int = 180,
) -> list[Section]:
    """Fallback: split transcript into even time-based sections."""
    sections: list[Section] = []
    start = 0.0
    index = 1
    while start < video_duration_seconds:
        end = min(start + interval_seconds, float(video_duration_seconds))
        section_text = " ".join(
            s.text for s in transcript if start <= s.start < end
        )
        if section_text.strip():
            sections.append(
                Section(
                    index=index,
                    title=f"Part {index}",
                    start_seconds=start,
                    end_seconds=end,
                    transcript_text=section_text,
                )
            )
            index += 1
        start = end
    return sections

"""Summarize video sections for infographic generation."""

import json

from google import genai
from google.genai import types

from yt_slides.models import Section, SectionSummary


def summarize_section(
    client: genai.Client,
    section: Section,
    video_title: str,
    total_sections: int,
    max_words: int = 350,
    model: str = "gemini-2.5-flash",
) -> SectionSummary:
    """Summarize a section into infographic-ready content."""
    duration_min = (section.end_seconds - section.start_seconds) / 60

    prompt = f"""You are creating content for an infographic slide. Summarize this section of a
YouTube video into visual-friendly content.

Video: {video_title}
Section {section.index}/{total_sections}: {section.title}
Duration: {duration_min:.1f} minutes

TRANSCRIPT:
{section.transcript_text}

Create a summary optimized for a single infographic image. The infographic will
contain text rendered directly in the image, so keep everything concise.

Provide a JSON object with:
- headline: A punchy 3-7 word title for this slide (will be the largest text)
- key_points: Array of 3-6 bullet points, each under 12 words
- summary: 1-2 sentences providing context (under 40 words total)
- visual_suggestions: Describe 1-2 visual metaphors, icons, or imagery that
  would enhance understanding of this content

CRITICAL: Total word count across all fields must stay under {max_words} words.

Return JSON: {{"headline": "...", "key_points": [...], "summary": "...", "visual_suggestions": "..."}}"""

    response = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    data = json.loads(response.text)
    visual = data["visual_suggestions"]
    if isinstance(visual, list):
        visual = "; ".join(visual)
    return SectionSummary(
        section=section,
        headline=data["headline"],
        key_points=data["key_points"],
        summary=data["summary"],
        visual_suggestions=visual,
    )

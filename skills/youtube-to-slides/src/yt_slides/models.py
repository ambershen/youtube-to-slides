"""Shared data models for the yt-slides pipeline."""

from pydantic import BaseModel


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    description: str
    channel_title: str
    duration_seconds: int
    tags: list[str] = []


class TranscriptSnippet(BaseModel):
    text: str
    start: float
    duration: float


class Chapter(BaseModel):
    title: str
    start_seconds: float
    end_seconds: float


class Section(BaseModel):
    index: int
    title: str
    start_seconds: float
    end_seconds: float
    transcript_text: str


class SectionSummary(BaseModel):
    section: Section
    headline: str
    key_points: list[str]
    summary: str
    visual_suggestions: str


class InfographicResult(BaseModel):
    section_index: int
    section_title: str
    image_path: str
    prompt_used: str

"""Fetch video metadata via YouTube Data API v3."""

import re

from googleapiclient.discovery import build

from yt_slides.models import VideoMetadata


def _parse_iso8601_duration(duration: str) -> int:
    """Convert ISO 8601 duration (PT1H23M45S) to total seconds."""
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration
    )
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_metadata(video_id: str, api_key: str) -> VideoMetadata:
    """Fetch video metadata from YouTube Data API v3."""
    youtube = build("youtube", "v3", developerKey=api_key)
    response = (
        youtube.videos()
        .list(part="snippet,contentDetails", id=video_id)
        .execute()
    )

    items = response.get("items", [])
    if not items:
        raise ValueError(f"Video not found: {video_id}")

    snippet = items[0]["snippet"]
    content = items[0]["contentDetails"]

    return VideoMetadata(
        video_id=video_id,
        title=snippet["title"],
        description=snippet.get("description", ""),
        channel_title=snippet.get("channelTitle", ""),
        duration_seconds=_parse_iso8601_duration(content["duration"]),
        tags=snippet.get("tags", []),
    )

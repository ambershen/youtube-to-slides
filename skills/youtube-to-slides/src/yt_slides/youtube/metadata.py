"""Fetch video metadata via yt-dlp (no API key required)."""

import yt_dlp

from yt_slides.models import VideoMetadata


def fetch_metadata(video_id: str) -> VideoMetadata:
    """Fetch video metadata using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError(f"Video not found: {video_id}")

    return VideoMetadata(
        video_id=video_id,
        title=info.get("title", ""),
        description=info.get("description", ""),
        channel_title=info.get("channel", "") or info.get("uploader", ""),
        duration_seconds=int(info.get("duration", 0)),
        tags=info.get("tags") or [],
    )

"""Extract YouTube video ID from various URL formats."""

import re
from urllib.parse import parse_qs, urlparse


_VIDEO_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL or bare ID string.

    Supports:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID
      - https://www.youtube.com/v/VIDEO_ID
      - Bare 11-character video ID
    """
    url = url.strip()

    # Bare video ID
    if _VIDEO_ID_RE.match(url):
        return url

    parsed = urlparse(url)

    # youtu.be/VIDEO_ID
    if parsed.hostname in ("youtu.be",):
        video_id = parsed.path.lstrip("/")
        if _VIDEO_ID_RE.match(video_id):
            return video_id

    # youtube.com/watch?v=VIDEO_ID
    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            video_id = qs.get("v", [None])[0]
            if video_id and _VIDEO_ID_RE.match(video_id):
                return video_id

        # /embed/VIDEO_ID or /v/VIDEO_ID
        for prefix in ("/embed/", "/v/"):
            if parsed.path.startswith(prefix):
                video_id = parsed.path[len(prefix):].split("/")[0]
                if _VIDEO_ID_RE.match(video_id):
                    return video_id

    raise ValueError(
        f"Could not extract video ID from: {url}\n"
        "Supported formats: youtube.com/watch?v=ID, youtu.be/ID, or bare 11-char ID"
    )

"""Fetch video transcript via youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi

from yt_slides.models import TranscriptSnippet


def fetch_transcript(video_id: str, language: str = "en") -> list[TranscriptSnippet]:
    """Fetch timestamped transcript for a YouTube video.

    Tries manual captions first, then auto-generated, then translation.
    Raises an exception if no transcript is available.
    """
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=[language, "en"])

    return [
        TranscriptSnippet(
            text=entry.text,
            start=entry.start,
            duration=entry.duration,
        )
        for entry in transcript.snippets
    ]

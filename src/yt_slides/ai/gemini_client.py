"""Shared Gemini API client."""

from google import genai


def create_client(api_key: str) -> genai.Client:
    """Create a configured Gemini API client."""
    return genai.Client(api_key=api_key)

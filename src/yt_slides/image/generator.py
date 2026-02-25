"""Generate infographic images using Gemini 2.5 Flash Image (Nano Banana)."""

from __future__ import annotations

import time
from pathlib import Path

from google import genai
from google.genai import types


class ImageGenerationError(Exception):
    """Raised when image generation fails after retries."""


def generate_infographic(
    client: genai.Client,
    prompt: str,
    output_path: Path,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    max_retries: int = 2,
) -> Path:
    """Generate an infographic image and save it to disk.

    Uses exponential backoff on failure. Returns the path to the saved image.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt + f"\n\nGenerate this as an image with {aspect_ratio} aspect ratio."],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    output_path.write_bytes(image_bytes)
                    return output_path

            raise ImageGenerationError("No image data in response")

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2.0 * (2**attempt))

    raise ImageGenerationError(
        f"Image generation failed after {max_retries + 1} attempts: {last_error}"
    )

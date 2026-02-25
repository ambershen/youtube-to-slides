"""Configuration management via environment variables and .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    youtube_api_key: str = ""

    # Gemini model settings
    gemini_text_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"

    # Image generation settings
    image_aspect_ratio: str = "16:9"

    # Output settings
    output_dir: Path = Path("./output")
    image_format: str = "png"

    # Pipeline settings
    max_sections: int = 0  # 0 = unlimited
    max_words_per_infographic: int = 350

    model_config = {"env_file": ".env", "env_prefix": ""}

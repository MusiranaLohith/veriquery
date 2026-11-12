
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Locate the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load environment variables from the project root.
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Application configuration for Gemini integration."""

    gemini_api_key: str
    request_timeout: int = 120
    max_retries: int = 2


def get_settings() -> Settings:
    """Load and validate application settings."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to the project-root .env file."
        )

    return Settings(gemini_api_key=api_key)


import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


Provider = Literal["gemini", "groq"]


def get_api_key(provider: Provider) -> str:
    """Load and validate the API key for the selected provider."""

    environment_variables = {
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
    }

    environment_variable = environment_variables[provider]
    api_key = os.getenv(environment_variable)

    if not api_key:
        raise ValueError(
            f"{environment_variable} is missing. "
            "Add it to the project-root .env file."
        )

    return api_key


@dataclass(frozen=True)
class Settings:
    """Gemini-specific request configuration."""

    gemini_api_key: str
    request_timeout: int = 120
    max_retries: int = 2


def get_settings() -> Settings:
    """Load Gemini settings."""

    return Settings(
        gemini_api_key=get_api_key("gemini"),
    )

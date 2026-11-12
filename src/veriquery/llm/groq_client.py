
import os
import json
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv
from groq import Groq
from groq import APIStatusError, APITimeoutError
from pydantic import ValidationError

from veriquery.llm.client import GenerationResult
from veriquery.llm.models import SQLGenerationResponse



MODEL_ID = "qwen/qwen3.8-27b"


def build_response_schema() -> dict:
    """Build a strict JSON Schema compatible with Groq."""

    schema = SQLGenerationResponse.model_json_schema()

    # Strict structured outputs require every property to be required.
    schema["required"] = list(schema["properties"].keys())
    schema["additionalProperties"] = False

    return schema


def classify_groq_error(error: Exception) -> str:
    """Classify Groq failures for experiment tracking."""

    if isinstance(error, APITimeoutError):
        return "timeout"

    if isinstance(error, APIStatusError):
        if error.status_code == 429:
            return "rate_limited"

        if error.status_code == 503:
            return "service_unavailable"

        if error.status_code in (408, 504):
            return "timeout"

        return "api_error"

    if isinstance(error, (ValidationError, ValueError, json.JSONDecodeError)):
        return "invalid_response"

    return "client_error"


class GroqSQLClient:
    """Generate structured SQL responses using Groq."""


    def __init__(
        self,
        api_key: str | None = None,
        request_timeout: int = 45,
    ):
        if api_key is None:
            project_root = Path(__file__).resolve().parents[3]
            load_dotenv(project_root / ".env")
            api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. "
                "Add it to the project-root .env file."
            )

        self.client = Groq(
            api_key=api_key,
            timeout=request_timeout,
            max_retries=0,
        )

    def generate(self, prompt: str) -> GenerationResult:
        """Generate one structured response without automatic retries."""

        start_time = perf_counter()

        try:
            response = self.client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_completion_tokens=1024,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "sql_generation_response",
                        "strict": True,
                        "schema": build_response_schema(),
                    },
                },
            )

            latency = perf_counter() - start_time

            if not response.choices:
                raise ValueError("Groq returned no response choices.")

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Groq returned empty response content.")

            parsed_output = SQLGenerationResponse.model_validate_json(
                content
            )

            usage = response.usage

            return GenerationResult(
                output=parsed_output,
                model_id=MODEL_ID,
                latency_seconds=latency,
                prompt_tokens=(
                    usage.prompt_tokens if usage else None
                ),
                candidate_tokens=(
                    usage.completion_tokens if usage else None
                ),
                total_tokens=(
                    usage.total_tokens if usage else None
                ),
                api_status="success",
            )

        except Exception as error:
            latency = perf_counter() - start_time

            return GenerationResult(
                output=None,
                model_id=MODEL_ID,
                latency_seconds=latency,
                prompt_tokens=None,
                candidate_tokens=None,
                total_tokens=None,
                api_status=classify_groq_error(error),
                error=f"{type(error).__name__}: {error}",
            )

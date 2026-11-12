
from google import genai
from google.genai import types

from google.genai.errors import APIError
from pydantic import ValidationError

from dataclasses import dataclass
from time import perf_counter

from veriquery.llm.config import Settings, get_settings
from veriquery.llm.models import SQLGenerationResponse


MODEL_ID = "gemini-3.8-flash"


@dataclass
class GenerationResult:
    """Structured response and metadata from one generation attempt."""

    output: SQLGenerationResponse | None
    model_id: str
    latency_seconds: float
    prompt_tokens: int | None
    candidate_tokens: int | None
    total_tokens: int | None
    api_status: str
    error: str | None = None


def classify_error(error: Exception) -> str:
    """Classify generation failures for experiment tracking."""

    if isinstance(error, APIError):
        if error.code == 503:
            return "service_unavailable"
        if error.code == 504:
            return "timeout"
        if error.code == 429:
            return "rate_limited"
        return "api_error"

    if isinstance(error, TimeoutError):
        return "timeout"

    if isinstance(error, (ValidationError, ValueError)):
        return "invalid_response"

    return "client_error"


class GeminiSQLClient:
    """Client for generating structured SQL responses with Gemini."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

        http_options = types.HttpOptions(
            timeout=self.settings.request_timeout * 1000,
            retry_options=types.HttpRetryOptions(
                attempts=self.settings.max_retries + 1,
                initial_delay=1.0,
                max_delay=4.0,
                http_status_codes=[408, 429, 500, 502, 503, 504],
            ),
        )

        self.client = genai.Client(
            api_key=self.settings.gemini_api_key,
            http_options=http_options,
        )

    def generate(self, prompt: str) -> GenerationResult:
        """Generate SQL and capture both success and failure metadata."""

        start_time = perf_counter()

        try:
            response = self.client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SQLGenerationResponse,
                ),
            )

            latency = perf_counter() - start_time

            if response.parsed is None:
                raise ValueError(
                    "Gemini returned no valid structured response."
                )

            parsed_output = SQLGenerationResponse.model_validate(
                response.parsed
            )

            usage = response.usage_metadata

            return GenerationResult(
                output=parsed_output,
                model_id=MODEL_ID,
                latency_seconds=latency,
                prompt_tokens=(
                    usage.prompt_token_count if usage else None
                ),
                candidate_tokens=(
                    usage.candidates_token_count if usage else None
                ),
                total_tokens=(
                    usage.total_token_count if usage else None
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
                api_status=classify_error(error),
                error=f"{type(error).__name__}: {error}",
            )

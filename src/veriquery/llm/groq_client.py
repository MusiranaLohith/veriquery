import json
from time import perf_counter

from groq import Groq
from groq import APIStatusError, APITimeoutError
from pydantic import ValidationError

from veriquery.llm.config import get_api_key
from veriquery.llm.client import GenerationResult
from veriquery.llm.models import SQLGenerationResponse


MODEL_ID = "qwen/qwen3.8-27b"

RATE_LIMIT_HEADER_NAMES = (
    "retry-after",
    "x-ratelimit-limit-requests",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-reset-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-tokens",
)


def build_response_schema() -> dict:
    """Build the response schema for local inspection and testing."""

    schema = SQLGenerationResponse.model_json_schema()

    schema["required"] = list(schema["properties"].keys())
    schema["additionalProperties"] = False

    return schema


def extract_rate_limit_headers(headers) -> dict[str, str]:
    """Extract available rate-limit headers from an HTTP response."""

    if headers is None:
        return {}

    extracted = {}

    for name in RATE_LIMIT_HEADER_NAMES:
        value = headers.get(name)

        if value is not None:
            extracted[name] = str(value)

    return extracted


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

    if isinstance(
        error,
        (ValidationError, ValueError, json.JSONDecodeError),
    ):
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
            api_key = get_api_key("groq")

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
        rate_limit_headers = {}

        try:
            raw_response = (
                self.client.chat.completions.with_raw_response.create(
                    model=MODEL_ID,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    reasoning_effort="none",
                    reasoning_format="hidden",
                    max_completion_tokens=2048,
                    response_format={
                        "type": "json_object",
                    },
                )
            )

            rate_limit_headers = extract_rate_limit_headers(
                raw_response.headers
            )

            response = raw_response.parse()

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
            finish_reason = response.choices[0].finish_reason

            return GenerationResult(
                output=parsed_output,
                model_id=MODEL_ID,
                latency_seconds=latency,
                finish_reason=finish_reason,
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
                rate_limit_headers=rate_limit_headers,
            )

        except Exception as error:
            latency = perf_counter() - start_time

            if isinstance(error, APIStatusError):
                error_response = getattr(error, "response", None)

                rate_limit_headers = extract_rate_limit_headers(
                    getattr(error_response, "headers", None)
                )

            return GenerationResult(
                output=None,
                model_id=MODEL_ID,
                latency_seconds=latency,
                prompt_tokens=None,
                candidate_tokens=None,
                total_tokens=None,
                api_status=classify_groq_error(error),
                error=f"{type(error).__name__}: {error}",
                rate_limit_headers=rate_limit_headers,
            )
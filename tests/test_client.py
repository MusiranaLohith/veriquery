from google.genai.errors import APIError
from unittest.mock import MagicMock, patch

from veriquery.llm.client import GeminiSQLClient
from veriquery.llm.models import SQLGenerationResponse


def create_client():
    """Create a client without making a real API connection."""
    return GeminiSQLClient(
        settings=MagicMock(gemini_api_key="fake-test-key")
    )


def test_generate_success():
    client = create_client()

    expected_output = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) FROM retail_transactions;",
        interpretation="Count transaction records.",
        assumptions=[],
        needs_clarification=False,
    )

    mock_response = MagicMock()
    mock_response.parsed = expected_output
    mock_response.usage_metadata.prompt_token_count = 100
    mock_response.usage_metadata.candidates_token_count = 50
    mock_response.usage_metadata.total_token_count = 150

    with patch.object(
        client.client.models,
        "generate_content",
        return_value=mock_response,
    ):
        result = client.generate("Count transaction records.")

    assert result.api_status == "success"
    assert result.output == expected_output
    assert result.total_tokens == 150
    assert result.error is None


def test_generate_api_failure():
    client = create_client()

    with patch.object(
        client.client.models,
        "generate_content",
        side_effect=RuntimeError("Simulated API failure"),
    ):
        result = client.generate("Count transaction records.")

    assert result.api_status == "client_error"
    assert result.output is None
    assert "Simulated API failure" in result.error


def test_generate_missing_structured_response():
    client = create_client()

    mock_response = MagicMock()
    mock_response.parsed = None

    with patch.object(
        client.client.models,
        "generate_content",
        return_value=mock_response,
    ):
        result = client.generate("Count transaction records.")

    assert result.api_status == "invalid_response"
    assert result.output is None
    assert "no valid structured response" in result.error


def test_generate_missing_token_usage():
    client = create_client()

    expected_output = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) FROM retail_transactions;",
        interpretation="Count transaction records.",
        assumptions=[],
        needs_clarification=False,
    )

    mock_response = MagicMock()
    mock_response.parsed = expected_output
    mock_response.usage_metadata = None

    with patch.object(
        client.client.models,
        "generate_content",
        return_value=mock_response,
    ):
        result = client.generate("Count transaction records.")

    assert result.api_status == "success"
    assert result.prompt_tokens is None
    assert result.candidate_tokens is None
    assert result.total_tokens is None


def test_classify_service_unavailable():
    from veriquery.llm.client import classify_error

    error = APIError(
        code=503,
        response_json={"error": {"message": "Service unavailable"}},
    )

    assert classify_error(error) == "service_unavailable"


def test_classify_timeout():
    from veriquery.llm.client import classify_error

    error = APIError(
        code=504,
        response_json={"error": {"message": "Deadline exceeded"}},
    )

    assert classify_error(error) == "timeout"


def test_classify_rate_limit():
    from veriquery.llm.client import classify_error

    error = APIError(
        code=429,
        response_json={"error": {"message": "Rate limit exceeded"}},
    )

    assert classify_error(error) == "rate_limited"
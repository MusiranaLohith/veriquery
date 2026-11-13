import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from groq import APIStatusError, APITimeoutError

from veriquery.llm.groq_client import (
    MODEL_ID,
    GroqSQLClient,
    build_response_schema,
    classify_groq_error,
)
from veriquery.llm.models import SQLGenerationResponse


def valid_response():
    return {
        "is_answerable": True,
        "sql": "SELECT COUNT(*) FROM retail_transactions;",
        "interpretation": "Count all retail transaction records.",
        "assumptions": [],
        "needs_clarification": False,
    }


def fake_groq_response(content):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason="stop",
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        ),
    )


def fake_raw_groq_response(content, headers=None):
    """Simulate the Groq raw HTTP response wrapper."""

    return SimpleNamespace(
        headers=headers or {},
        parse=lambda: fake_groq_response(content),
    )


def test_model_id_is_configured():
    assert MODEL_ID == "qwen/qwen3.8-27b"


def test_response_schema_contains_all_required_fields():
    schema = build_response_schema()

    assert set(schema["required"]) == {
        "is_answerable",
        "sql",
        "interpretation",
        "assumptions",
        "needs_clarification",
    }

    assert schema["additionalProperties"] is False


def test_response_schema_has_no_optional_properties():
    schema = build_response_schema()

    for property_name in schema["properties"]:
        assert property_name in schema["required"]


def test_client_rejects_missing_api_key():
    with patch.dict(
        "os.environ",
        {
            "GROQ_API_KEY": "",
        },
        clear=True,
    ):
        with pytest.raises(
            ValueError,
            match="GROQ_API_KEY is missing",
        ):
            GroqSQLClient()


def test_generate_success():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        fake_raw_groq_response(
            json.dumps(valid_response()),
            headers={
                "x-ratelimit-remaining-tokens": "5000",
                "x-ratelimit-reset-tokens": "2s",
            },
        )
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate a SQL query.")

    assert isinstance(result.output, SQLGenerationResponse)
    assert result.api_status == "success"
    assert result.model_id == MODEL_ID
    assert result.prompt_tokens == 100
    assert result.candidate_tokens == 50
    assert result.total_tokens == 150
    assert result.finish_reason == "stop"

    assert result.rate_limit_headers == {
        "x-ratelimit-remaining-tokens": "5000",
        "x-ratelimit-reset-tokens": "2s",
    }

    fake_client.chat.completions.with_raw_response.create.assert_called_once()


def test_generate_sends_json_object_mode():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        fake_raw_groq_response(
            json.dumps(valid_response())
        )
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        client.generate("Generate SQL.")

    call_args = (
        fake_client.chat.completions.with_raw_response.create.call_args.kwargs
    )

    assert call_args["reasoning_effort"] == "none"
    assert call_args["reasoning_format"] == "hidden"
    assert call_args["max_completion_tokens"] == 1024

    assert call_args["response_format"] == {
        "type": "json_object",
    }


def test_generate_captures_only_available_rate_limit_headers():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        fake_raw_groq_response(
            json.dumps(valid_response()),
            headers={
                "retry-after": "10",
                "x-ratelimit-remaining-requests": "25",
                "unrelated-header": "ignore-me",
            },
        )
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.rate_limit_headers == {
        "retry-after": "10",
        "x-ratelimit-remaining-requests": "25",
    }


def test_generate_rejects_invalid_structured_response():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        fake_raw_groq_response(
            '{"is_answerable": true, "sql": null}'
        )
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "invalid_response"


def test_generate_handles_empty_response():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        fake_raw_groq_response("")
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "invalid_response"


def test_generate_handles_empty_choices():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.return_value = (
        SimpleNamespace(
            headers={},
            parse=lambda: SimpleNamespace(
                choices=[],
                usage=None,
            ),
        )
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "invalid_response"


def test_generate_captures_rate_limit_headers_from_429():
    fake_client = MagicMock()

    response = MagicMock()
    response.status_code = 429
    response.headers = {
        "retry-after": "30",
        "x-ratelimit-remaining-tokens": "0",
        "x-ratelimit-reset-tokens": "30s",
    }

    error = APIStatusError(
        "Rate limit exceeded",
        response=response,
        body=None,
    )

    fake_client.chat.completions.with_raw_response.create.side_effect = (
        error
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "rate_limited"
    assert result.rate_limit_headers == {
        "retry-after": "30",
        "x-ratelimit-remaining-tokens": "0",
        "x-ratelimit-reset-tokens": "30s",
    }


def test_generate_handles_api_error_without_response():
    fake_client = MagicMock()

    response = MagicMock()
    response.status_code = 429

    error = APIStatusError(
        "Rate limit exceeded",
        response=response,
        body=None,
    )

    error.response = None

    fake_client.chat.completions.with_raw_response.create.side_effect = (
        error
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "rate_limited"
    assert result.rate_limit_headers == {}


def test_classify_timeout():
    error = APITimeoutError(request=MagicMock())

    assert classify_groq_error(error) == "timeout"


def test_classify_rate_limit():
    response = MagicMock()
    response.status_code = 429

    error = APIStatusError(
        "Rate limit exceeded",
        response=response,
        body=None,
    )

    assert classify_groq_error(error) == "rate_limited"


def test_classify_service_unavailable():
    response = MagicMock()
    response.status_code = 503

    error = APIStatusError(
        "Service unavailable",
        response=response,
        body=None,
    )

    assert classify_groq_error(error) == "service_unavailable"


def test_generate_does_not_retry_automatically():
    fake_client = MagicMock()

    fake_client.chat.completions.with_raw_response.create.side_effect = (
        RuntimeError("Simulated failure")
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ) as mock_groq:
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "client_error"

    mock_groq.assert_called_once_with(
        api_key="test-key",
        timeout=45,
        max_retries=0,
    )

    fake_client.chat.completions.with_raw_response.create.assert_called_once()
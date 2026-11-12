
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
                message=SimpleNamespace(content=content)
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        ),
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

    for property_name, property_schema in schema["properties"].items():
        assert property_name in schema["required"]


def test_client_rejects_missing_api_key():
    with patch.dict("os.environ", {}, clear=True):
        with patch(
            "veriquery.llm.groq_client.load_dotenv"
        ):
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                GroqSQLClient()


def test_generate_success():
    fake_client = MagicMock()

    fake_client.chat.completions.create.return_value = (
        fake_groq_response(
            json.dumps(valid_response())
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

    fake_client.chat.completions.create.assert_called_once()


def test_generate_sends_strict_json_schema():
    fake_client = MagicMock()

    fake_client.chat.completions.create.return_value = (
        fake_groq_response(
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
        fake_client.chat.completions.create.call_args.kwargs
    )

    response_format = call_args["response_format"]

    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert response_format["json_schema"]["name"] == (
        "sql_generation_response"
    )
    assert call_args["max_completion_tokens"] == 1024


def test_generate_rejects_invalid_structured_response():
    fake_client = MagicMock()

    fake_client.chat.completions.create.return_value = (
        fake_groq_response(
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

    fake_client.chat.completions.create.return_value = (
        fake_groq_response("")
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

    fake_client.chat.completions.create.return_value = (
        SimpleNamespace(choices=[], usage=None)
    )

    with patch(
        "veriquery.llm.groq_client.Groq",
        return_value=fake_client,
    ):
        client = GroqSQLClient(api_key="test-key")
        result = client.generate("Generate SQL.")

    assert result.output is None
    assert result.api_status == "invalid_response"


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

    fake_client.chat.completions.create.side_effect = RuntimeError(
        "Simulated failure"
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

    fake_client.chat.completions.create.assert_called_once()

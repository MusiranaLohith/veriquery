
import pytest
from pydantic import ValidationError

from veriquery.llm.models import SQLGenerationResponse


def test_valid_answerable_response():
    response = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) FROM retail_transactions;",
        interpretation="Count all transaction records.",
        assumptions=[],
        needs_clarification=False,
    )

    assert response.is_answerable is True
    assert response.sql is not None


def test_valid_unanswerable_response():
    response = SQLGenerationResponse(
        is_answerable=False,
        sql=None,
        interpretation="Calculate net profit by product.",
        assumptions=[],
        needs_clarification=False,
    )

    assert response.is_answerable is False
    assert response.sql is None


def test_unanswerable_response_cannot_contain_sql():
    with pytest.raises(ValidationError):
        SQLGenerationResponse(
            is_answerable=False,
            sql="SELECT * FROM retail_transactions;",
            interpretation="Unsupported question.",
            assumptions=[],
            needs_clarification=False,
        )


def test_answerable_response_requires_sql():
    with pytest.raises(ValidationError):
        SQLGenerationResponse(
            is_answerable=True,
            sql=None,
            interpretation="Count transaction records.",
            assumptions=[],
            needs_clarification=False,
        )


def test_answerable_response_rejects_empty_sql():
    with pytest.raises(ValidationError):
        SQLGenerationResponse(
            is_answerable=True,
            sql="   ",
            interpretation="Count transaction records.",
            assumptions=[],
            needs_clarification=False,
        )


def test_answerable_response_requiring_clarification_must_not_contain_sql():
    with pytest.raises(ValidationError, match="requiring clarification"):
        SQLGenerationResponse(
            is_answerable=True,
            sql="SELECT COUNT(*) FROM retail_transactions;",
            interpretation="The question needs clarification.",
            assumptions=[],
            needs_clarification=True,
        )


def test_answerable_response_requiring_clarification_can_have_null_sql():
    response = SQLGenerationResponse(
        is_answerable=True,
        sql=None,
        interpretation="The question needs clarification.",
        assumptions=[],
        needs_clarification=True,
    )

    assert response.is_answerable is True
    assert response.needs_clarification is True
    assert response.sql is None


def test_unanswerable_response_can_require_clarification():
    response = SQLGenerationResponse(
        is_answerable=False,
        sql=None,
        interpretation="The requested information is unavailable.",
        assumptions=[],
        needs_clarification=True,
    )

    assert response.is_answerable is False
    assert response.needs_clarification is True
    assert response.sql is None

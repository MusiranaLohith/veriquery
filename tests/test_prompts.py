
import pytest

from veriquery.llm.prompts import (
    PROMPT_VERSION,
    DATABASE_SCHEMA,
    BUSINESS_RULES,
    SYSTEM_INSTRUCTIONS,
    build_prompt,
)


def test_prompt_has_version():
    assert PROMPT_VERSION == "full-schema-baseline-v1"


def test_prompt_contains_complete_schema():
    prompt = build_prompt("Count all records.")

    assert DATABASE_SCHEMA in prompt

    expected_columns = [
        "record_id BIGINT",
        "invoice TEXT",
        "stock_code TEXT",
        "description TEXT",
        "quantity INTEGER",
        "invoice_date TIMESTAMP",
        "price NUMERIC(12, 3)",
        "customer_id BIGINT",
        "country TEXT",
        "source_sheet TEXT",
    ]

    for column in expected_columns:
        assert column in prompt


def test_prompt_contains_business_rules():
    prompt = build_prompt("Calculate total quantity.")

    assert BUSINESS_RULES in prompt
    assert "negative quantity" in prompt
    assert "per-unit GBP value" in prompt
    assert "Net profit cannot be calculated from this schema alone." in prompt


def test_prompt_contains_system_instructions():
    prompt = build_prompt("Count all invoices.")

    assert SYSTEM_INSTRUCTIONS in prompt
    assert "SELECT" in prompt
    assert "Never invent tables, columns" in prompt


def test_prompt_includes_user_question():
    question = "Which country has the most transaction records?"

    prompt = build_prompt(question)

    assert question in prompt


def test_prompt_rejects_empty_question():
    with pytest.raises(ValueError):
        build_prompt("")


def test_prompt_rejects_whitespace_question():
    with pytest.raises(ValueError):
        build_prompt("   ")


def test_prompt_does_not_include_retrieved_examples():
    prompt = build_prompt("Count all records.")

    assert "Retrieved SQL examples:" not in prompt
    assert "Retrieved context:" not in prompt

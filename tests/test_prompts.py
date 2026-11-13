
import pytest

from veriquery.llm.prompts import (
    BUSINESS_RULES,
    DATABASE_SCHEMA,
    PROMPT_VERSION,
    SYSTEM_INSTRUCTIONS,
    build_prompt,
)


def test_prompt_version():
    assert PROMPT_VERSION == "full-schema-baseline-json-object-v3"


def test_database_schema_contains_database_name():
    assert "Database: veriquery" in DATABASE_SCHEMA


def test_database_schema_contains_retail_transactions():
    assert "Table: retail_transactions" in DATABASE_SCHEMA


def test_database_schema_contains_required_columns():
    required_columns = [
        "record_id",
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "price",
        "customer_id",
        "country",
        "source_sheet",
    ]

    for column in required_columns:
        assert column in DATABASE_SCHEMA


def test_database_schema_declares_single_table():
    assert "There is only one table." in DATABASE_SCHEMA


def test_business_rules_include_all_verified_rules():
    assert "Verified business definitions" in BUSINESS_RULES
    assert "No verified cost field or profit" in BUSINESS_RULES


def test_system_instructions_require_postgresql():
    assert "Generate PostgreSQL SQL only." in SYSTEM_INSTRUCTIONS


def test_system_instructions_require_read_only_sql():
    assert "Generate one read-only analytical query." in SYSTEM_INSTRUCTIONS
    assert "Never generate INSERT, UPDATE, DELETE" in SYSTEM_INSTRUCTIONS


def test_system_instructions_prohibit_invented_schema():
    assert "Never invent tables, columns, relationships, or data." in SYSTEM_INSTRUCTIONS


def test_system_instructions_prohibit_multi_table_claims():
    assert "Do not claim multi-table JOIN capability." in SYSTEM_INSTRUCTIONS


def test_prompt_includes_aggregation_scope_guidance():
    assert "A WHERE clause filters rows before all SELECT aggregates" in SYSTEM_INSTRUCTIONS
    assert "conditional aggregation with FILTER or CASE" in SYSTEM_INSTRUCTIONS


def test_prompt_includes_null_handling_guidance():
    assert "COUNT(DISTINCT column) ignores NULL values" in SYSTEM_INSTRUCTIONS
    assert "Do not discard rows with NULL customer_id" in SYSTEM_INSTRUCTIONS


def test_prompt_includes_calendar_month_guidance():
    assert "January 2010 and January 2011 are separate" in SYSTEM_INSTRUCTIONS
    assert "DATE_TRUNC('month', invoice_date)" in SYSTEM_INSTRUCTIONS


def test_prompt_includes_zero_match_group_guidance():
    assert "exclude groups with zero qualifying records" in SYSTEM_INSTRUCTIONS


def test_prompt_includes_postgresql_function_guidance():
    assert "Do not use MONTH() or YEAR()" in SYSTEM_INSTRUCTIONS


def test_prompt_requires_assumptions_to_match_sql():
    assert "Assumptions must accurately match the SQL." in SYSTEM_INSTRUCTIONS


def test_prompt_requires_json_object_output():
    required_keys = [
        '"is_answerable"',
        '"sql"',
        '"interpretation"',
        '"assumptions"',
        '"needs_clarification"',
    ]

    for key in required_keys:
        assert key in SYSTEM_INSTRUCTIONS


def test_prompt_does_not_include_retrieval():
    prompt = build_prompt("Show total transaction records.")

    assert "BM25" not in prompt
    assert "dense retrieval" not in prompt
    assert "retrieved examples" not in prompt.lower()


def test_build_prompt_includes_schema_and_business_rules():
    prompt = build_prompt("Show total transaction records.")

    assert DATABASE_SCHEMA in prompt
    assert BUSINESS_RULES in prompt
    assert SYSTEM_INSTRUCTIONS in prompt


def test_build_prompt_includes_question():
    question = "Which country has the most transaction records?"

    prompt = build_prompt(question)

    assert question in prompt


@pytest.mark.parametrize("question", ["", " ", "\n", "\t"])
def test_build_prompt_rejects_empty_questions(question):
    with pytest.raises(ValueError):
        build_prompt(question)


@pytest.mark.parametrize("question", [None, 123, [], {}])
def test_build_prompt_rejects_non_string_questions(question):
    with pytest.raises(ValueError):
        build_prompt(question)



def test_business_rules_include_operational_entry_stock_codes():
    from veriquery.llm.prompts import BUSINESS_RULES

    codes = [
        "'M'", "'POST'", "'D'", "'BANK CHARGES'",
        "'AMAZONFEE'", "'ADJUST'", "'CRUK'", "'C2'",
        "'DOT'", "'ADJUST2'", "'B'", "'m'",
    ]

    for code in codes:
        assert code in BUSINESS_RULES

    assert "'M'" in BUSINESS_RULES
    assert "'m'" in BUSINESS_RULES
    assert "distinct codes" in BUSINESS_RULES

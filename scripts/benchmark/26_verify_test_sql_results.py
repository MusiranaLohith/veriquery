
import json
import math
import getpass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "locked_test"
    / "test_questions.jsonl"
)

ANSWER_KEY_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "locked_test"
    / "test_answer_key.jsonl"
)


# --------------------------------------------------
# 2. Database configuration
# --------------------------------------------------

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "veriquery",
    "user": "veriquery_loader",
}


# --------------------------------------------------
# 3. Result conversion and comparison
# --------------------------------------------------

def make_json_compatible(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def results_match(expected, actual, path="result"):
    """
    Recursively compare expected and actual results.

    - Dictionary keys and values must match.
    - Lists must match in both contents and ordering.
    - Floating-point values use a small tolerance.
    - Other values require equality.
    """

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False, f"{path}: expected dictionary"

        if expected.keys() != actual.keys():
            return False, (
                f"{path}: column mismatch; "
                f"expected {list(expected.keys())}, "
                f"actual {list(actual.keys())}"
            )

        for key in expected:
            matched, message = results_match(
                expected[key],
                actual[key],
                f"{path}.{key}",
            )
            if not matched:
                return False, message

        return True, "Match"

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False, f"{path}: expected list"

        if len(expected) != len(actual):
            return False, (
                f"{path}: row-count mismatch; "
                f"expected {len(expected)}, "
                f"actual {len(actual)}"
            )

        for index, (expected_item, actual_item) in enumerate(
            zip(expected, actual)
        ):
            matched, message = results_match(
                expected_item,
                actual_item,
                f"{path}[{index}]",
            )
            if not matched:
                return False, message

        return True, "Match"

    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected == actual, (
            "Match" if expected == actual
            else f"{path}: expected {expected!r}, got {actual!r}"
        )

    if (
        isinstance(expected, (int, float))
        and isinstance(actual, (int, float))
    ):
        matched = math.isclose(
            expected,
            actual,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        return matched, (
            "Match" if matched
            else f"{path}: expected {expected!r}, got {actual!r}"
        )

    matched = expected == actual

    return matched, (
        "Match" if matched
        else f"{path}: expected {expected!r}, got {actual!r}"
    )


# --------------------------------------------------
# 4. Load benchmark files
# --------------------------------------------------

def load_jsonl(path):
    with path.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


# --------------------------------------------------
# 5. Main verification
# --------------------------------------------------

def main():

    questions = load_jsonl(QUESTIONS_PATH)
    answer_keys = load_jsonl(ANSWER_KEY_PATH)

    questions_by_id = {
        item["question_id"]: item
        for item in questions
    }

    answer_keys_by_id = {
        item["question_id"]: item
        for item in answer_keys
    }

    answerable_ids = {
        question_id
        for question_id, question in questions_by_id.items()
        if question["answerability"] == "answerable"
    }

    unanswerable_ids = {
        question_id
        for question_id, question in questions_by_id.items()
        if question["answerability"] == "unanswerable"
    }

    if len(questions) != 60:
        raise ValueError(
            f"Expected 60 questions, found {len(questions)}"
        )

    if len(answer_keys) != 60:
        raise ValueError(
            f"Expected 60 answer keys, found {len(answer_keys)}"
        )

    if len(questions_by_id) != 60:
        raise ValueError("Duplicate question IDs detected.")

    if len(answer_keys_by_id) != 60:
        raise ValueError("Duplicate answer-key IDs detected.")

    if answerable_ids | unanswerable_ids != set(questions_by_id):
        raise ValueError("Unexpected answerability value detected.")

    if answerable_ids & unanswerable_ids:
        raise ValueError("Answerability classification overlap.")

    if set(answer_keys_by_id) != set(questions_by_id):
        raise ValueError("Question and answer-key IDs do not match.")

    print("=" * 75)
    print("LOCKED-TEST SQL AND EXPECTED-RESULT VERIFICATION")
    print("=" * 75)

    print(f"Total questions: {len(questions)}")
    print(f"Answerable questions: {len(answerable_ids)}")
    print(f"Unanswerable questions: {len(unanswerable_ids)}")

    password = getpass.getpass(
        "\nPostgreSQL password for veriquery_loader: "
    )

    passed = []
    failed = []

    with psycopg.connect(
        **DB_CONFIG,
        password=password,
        row_factory=dict_row,
    ) as connection:

        with connection.cursor() as cursor:

            # Prevent all database modifications.
            cursor.execute("SET TRANSACTION READ ONLY")

            for question_id in sorted(answerable_ids):

                answer_key = answer_keys_by_id[question_id]
                reference_sql = answer_key["reference_sql"]
                expected = answer_key["expected_result"]

                print(f"\nExecuting {question_id}...")

                try:
                    cursor.execute(reference_sql)
                    rows = cursor.fetchall()

                    actual_rows = [
                        {
                            key: make_json_compatible(value)
                            for key, value in row.items()
                        }
                        for row in rows
                    ]

                    if len(actual_rows) == 1:
                        actual = actual_rows[0]
                    else:
                        actual = actual_rows

                    matched, message = results_match(
                        expected,
                        actual,
                    )

                    if matched:
                        passed.append(question_id)
                        print("  PASS")
                    else:
                        failed.append((question_id, message))
                        print(f"  FAIL: {message}")

                except Exception as error:
                    failed.append(
                        (question_id, f"{type(error).__name__}: {error}")
                    )
                    print(f"  ERROR: {type(error).__name__}: {error}")

                    # Recover the transaction after a query error.
                    connection.rollback()

                    with connection.cursor() as recovery_cursor:
                        recovery_cursor.execute(
                            "SET TRANSACTION READ ONLY"
                        )

    # --------------------------------------------------
    # 6. Final report
    # --------------------------------------------------

    print("\n" + "=" * 75)
    print("VERIFICATION SUMMARY")
    print("=" * 75)

    print(f"Answerable queries: {len(answerable_ids)}")
    print(f"Passed: {len(passed)}")
    print(f"Failed: {len(failed)}")
    print(f"Unanswerable questions skipped: {len(unanswerable_ids)}")

    if failed:
        print("\nFAILED QUESTIONS:")
        for question_id, message in failed:
            print(f"{question_id}: {message}")

    print("\nUNANSWERABLE QUESTIONS:")
    for question_id in sorted(unanswerable_ids):
        print(f"{question_id}: correctly skipped")

    if len(passed) == len(answerable_ids) and not failed:
        print("\nTEST SQL VERIFICATION: PASSED")
    else:
        print("\nTEST SQL VERIFICATION: FAILED")


if __name__ == "__main__":
    main()

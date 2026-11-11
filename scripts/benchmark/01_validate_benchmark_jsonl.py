
import json
import sys
from collections import Counter
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEV_DIR = PROJECT_ROOT / "data" / "benchmark" / "dev"
TEST_DIR = PROJECT_ROOT / "data" / "benchmark" / "locked_test"


# --------------------------------------------------
# 2. CURRENT BENCHMARK EXPECTATIONS
# --------------------------------------------------

EXPECTED = {
    "dev": {
        "total": 40,
        "categories": {
            "schema_understanding": 4,
            "filtering_and_sorting": 4,
            "aggregation_and_grouping": 6,
            "date_and_time_analysis": 5,
            "null_handling": 4,
            "customer_country_analysis": 4,
            "product_operational_code_analysis": 4,
            "transaction_cancellation_analysis": 4,
            "multi_condition_analytical_reasoning": 4,
            "unanswerable_questions": 1,
        },
        "difficulties": {
            "easy": 15,
            "medium": 19,
            "hard": 6,
        },
        "answerability": {
            "answerable": 39,
            "unanswerable": 1,
        },
    },

    "test": {
        "total": 60,
        "categories": {
            "schema_understanding": 4,
            "filtering_and_sorting": 8,
            "aggregation_and_grouping": 8,
            "date_and_time_analysis": 4,
            "null_handling": 5,
            "customer_country_analysis": 6,
            "product_operational_code_analysis": 6,
            "transaction_cancellation_analysis": 8,
            "multi_condition_analytical_reasoning": 7,
            "unanswerable_questions": 4,
        },
        # Current working distribution, subject to final
        # difficulty-rubric review.
        "difficulties": {
            "easy": 10,
            "medium": 45,
            "hard": 5
        },
        "answerability": {
            "answerable": 56,
            "unanswerable": 4,
        },
    },
}


VALID_CATEGORIES = set(EXPECTED["dev"]["categories"])
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_ANSWERABILITY = {"answerable", "unanswerable"}


# --------------------------------------------------
# 3. JSONL LOADING
# --------------------------------------------------

def load_jsonl(file_path: Path) -> list[dict]:
    """Load JSONL and reject malformed or empty files."""

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    records = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {file_path}, "
                    f"line {line_number}: {error}"
                ) from error

            if not isinstance(record, dict):
                raise ValueError(
                    f"Expected JSON object in {file_path}, "
                    f"line {line_number}."
                )

            records.append(record)

    if not records:
        raise ValueError(f"File contains no records: {file_path}")

    return records


# --------------------------------------------------
# 4. QUESTION VALIDATION
# --------------------------------------------------

def validate_question_fields(questions: list[dict]) -> list[str]:

    required_fields = {
        "question_id",
        "question",
        "category",
        "difficulty",
        "answerability",
    }

    errors = []

    for index, question in enumerate(questions, start=1):
        missing = required_fields - question.keys()

        if missing:
            errors.append(
                f"Question record {index} missing fields: "
                f"{sorted(missing)}"
            )
            continue

        qid = question["question_id"]

        if not isinstance(qid, str) or not qid.strip():
            errors.append(f"Record {index} has invalid question_id.")
            continue

        if not isinstance(question["question"], str) or not question["question"].strip():
            errors.append(f"{qid} has an empty question.")

        if question["category"] not in VALID_CATEGORIES:
            errors.append(
                f"{qid} has invalid category: {question['category']}"
            )

        if question["difficulty"] not in VALID_DIFFICULTIES:
            errors.append(
                f"{qid} has invalid difficulty: {question['difficulty']}"
            )

        if question["answerability"] not in VALID_ANSWERABILITY:
            errors.append(
                f"{qid} has invalid answerability: "
                f"{question['answerability']}"
            )

    return errors


# --------------------------------------------------
# 5. QUESTION ID VALIDATION
# --------------------------------------------------

def validate_unique_ids(records: list[dict], label: str) -> list[str]:

    ids = [
        record.get("question_id")
        for record in records
    ]

    duplicates = [
        qid
        for qid, count in Counter(ids).items()
        if count > 1
    ]

    if duplicates:
        return [f"Duplicate {label} IDs: {sorted(duplicates)}"]

    return []


def validate_sequential_ids(
    questions: list[dict],
    prefix: str,
    expected_count: int,
) -> list[str]:

    expected_ids = [
        f"{prefix}{number:03d}"
        for number in range(1, expected_count + 1)
    ]

    actual_ids = [
        question.get("question_id")
        for question in questions
    ]

    if actual_ids != expected_ids:
        return [
            f"{prefix} IDs are not sequential from "
            f"{expected_ids[0]} to {expected_ids[-1]}."
        ]

    return []


# --------------------------------------------------
# 6. ANSWER KEY VALIDATION
# --------------------------------------------------

def validate_answer_keys(
    questions: list[dict],
    answer_keys: list[dict],
) -> list[str]:

    errors = []

    question_map = {
        question.get("question_id"): question
        for question in questions
    }

    answer_map = {
        answer.get("question_id"): answer
        for answer in answer_keys
    }

    question_ids = set(question_map)
    answer_ids = set(answer_map)

    missing = question_ids - answer_ids
    extra = answer_ids - question_ids

    if missing:
        errors.append(
            f"Questions without answer keys: {sorted(missing)}"
        )

    if extra:
        errors.append(
            f"Answer keys without questions: {sorted(extra)}"
        )

    for index, answer in enumerate(answer_keys, start=1):

        required = {
            "question_id",
            "reference_sql",
            "expected_result",
        }

        missing_fields = required - answer.keys()

        if missing_fields:
            errors.append(
                f"Answer key record {index} missing fields: "
                f"{sorted(missing_fields)}"
            )
            continue

        qid = answer["question_id"]

        sql = answer["reference_sql"]
        expected_result = answer["expected_result"]

        if not isinstance(sql, str) or not sql.strip():
            errors.append(f"{qid} has invalid reference_sql.")

        if expected_result is None:
            errors.append(f"{qid} has null expected_result.")

        question = question_map.get(qid)

        if question is None:
            continue

        answerability = question.get("answerability")

        if answerability == "unanswerable":
            note = answer.get("validation_note")

            if not isinstance(note, str) or not note.strip():
                errors.append(
                    f"{qid} is unanswerable but has no validation_note."
                )

        elif answerability == "answerable":
            if "validation_note" in answer:
                if not isinstance(answer["validation_note"], str):
                    errors.append(
                        f"{qid} has an invalid validation_note."
                    )

    return errors


# --------------------------------------------------
# 7. DISTRIBUTION VALIDATION
# --------------------------------------------------

def validate_distribution(
    questions: list[dict],
    split_name: str,
) -> list[str]:

    errors = []
    expected = EXPECTED[split_name]

    distributions = {
        "categories": "category",
        "difficulties": "difficulty",
        "answerability": "answerability",
    }

    for distribution_name, field_name in distributions.items():

        actual = Counter(
            question[field_name]
            for question in questions
            if field_name in question
        )

        expected_counts = Counter(
            expected[distribution_name]
        )

        if actual != expected_counts:
            errors.append(
                f"{split_name} {distribution_name} mismatch. "
                f"Expected: {dict(expected_counts)}; "
                f"Actual: {dict(actual)}"
            )

    return errors


# --------------------------------------------------
# 8. SPLIT VALIDATION
# --------------------------------------------------

def validate_split(
    split_name: str,
    questions: list[dict],
    answer_keys: list[dict],
) -> list[str]:

    errors = []

    prefix = "DEV" if split_name == "dev" else "TEST"
    expected_count = EXPECTED[split_name]["total"]

    errors.extend(
        validate_question_fields(questions)
    )

    errors.extend(
        validate_unique_ids(questions, f"{split_name} question")
    )

    errors.extend(
        validate_unique_ids(answer_keys, f"{split_name} answer")
    )

    errors.extend(
        validate_sequential_ids(
            questions,
            prefix,
            expected_count,
        )
    )

    errors.extend(
        validate_answer_keys(questions, answer_keys)
    )

    errors.extend(
        validate_distribution(questions, split_name)
    )

    if len(questions) != expected_count:
        errors.append(
            f"{split_name}: expected {expected_count} questions, "
            f"found {len(questions)}."
        )

    if len(answer_keys) != expected_count:
        errors.append(
            f"{split_name}: expected {expected_count} answer keys, "
            f"found {len(answer_keys)}."
        )

    return errors


# --------------------------------------------------
# 9. MAIN VALIDATION
# --------------------------------------------------

def validate_benchmark() -> int:

    files = {
        "dev_questions": DEV_DIR / "dev_questions.jsonl",
        "dev_answers": DEV_DIR / "dev_answer_key.jsonl",
        "test_questions": TEST_DIR / "test_questions.jsonl",
        "test_answers": TEST_DIR / "test_answer_key.jsonl",
    }

    try:
        dev_questions = load_jsonl(files["dev_questions"])
        dev_answers = load_jsonl(files["dev_answers"])

        test_questions = load_jsonl(files["test_questions"])
        test_answers = load_jsonl(files["test_answers"])

    except (FileNotFoundError, ValueError) as error:
        print("\nBENCHMARK VALIDATION: FAILED")
        print("-", error)
        return 1

    errors = []

    errors.extend(
        validate_split("dev", dev_questions, dev_answers)
    )

    errors.extend(
        validate_split("test", test_questions, test_answers)
    )

    dev_ids = {
        question.get("question_id")
        for question in dev_questions
    }

    test_ids = {
        question.get("question_id")
        for question in test_questions
    }

    overlap = dev_ids & test_ids

    if overlap:
        errors.append(
            f"Development/test ID overlap: {sorted(overlap)}"
        )

    print("\nDEVELOPMENT BENCHMARK")
    print("Questions:", len(dev_questions))
    print("Answer keys:", len(dev_answers))
    print(
        "Difficulty:",
        dict(Counter(q["difficulty"] for q in dev_questions))
    )

    print("\nLOCKED-TEST BENCHMARK")
    print("Questions:", len(test_questions))
    print("Answer keys:", len(test_answers))
    print(
        "Difficulty:",
        dict(Counter(q["difficulty"] for q in test_questions))
    )

    print("\nDevelopment/test ID overlap:", len(overlap))
    print("Total questions:", len(dev_questions) + len(test_questions))

    if errors:
        print("\nBENCHMARK VALIDATION: FAILED")

        for error in errors:
            print("-", error)

        return 1

    print("\nBENCHMARK VALIDATION: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(validate_benchmark())

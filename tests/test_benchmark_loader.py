
import json

import pytest

from veriquery.benchmark.loader import load_dev_questions


def create_record(question_id="DEV001"):
    return {
        "question_id": question_id,
        "question": "How many transaction records exist?",
        "category": "schema_understanding",
        "difficulty": "easy",
        "answerability": "answerable",
    }


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def test_load_valid_questions(tmp_path):
    path = tmp_path / "dev.jsonl"
    write_jsonl(path, [
        create_record("DEV001"),
        create_record("DEV002"),
    ])

    questions = load_dev_questions(path, expected_count=2)

    assert len(questions) == 2
    assert questions[0].question_id == "DEV001"
    assert questions[1].question_id == "DEV002"


def test_reject_missing_file(tmp_path):
    path = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError):
        load_dev_questions(path)


def test_reject_duplicate_question_ids(tmp_path):
    path = tmp_path / "dev.jsonl"
    write_jsonl(path, [
        create_record("DEV001"),
        create_record("DEV001"),
    ])

    with pytest.raises(ValueError, match="Duplicate question ID"):
        load_dev_questions(path, expected_count=2)


def test_reject_invalid_json(tmp_path):
    path = tmp_path / "dev.jsonl"
    path.write_text('{"question_id": invalid}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid benchmark record"):
        load_dev_questions(path, expected_count=1)


def test_reject_invalid_difficulty(tmp_path):
    path = tmp_path / "dev.jsonl"
    record = create_record()
    record["difficulty"] = "extreme"
    write_jsonl(path, [record])

    with pytest.raises(ValueError, match="Invalid benchmark record"):
        load_dev_questions(path, expected_count=1)


def test_reject_unexpected_question_count(tmp_path):
    path = tmp_path / "dev.jsonl"
    write_jsonl(path, [create_record("DEV001")])

    with pytest.raises(ValueError, match="Expected 40 questions"):
        load_dev_questions(path)

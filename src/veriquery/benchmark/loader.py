
import json
from pathlib import Path

from veriquery.benchmark.models import BenchmarkQuestion


def load_dev_questions(
    file_path: Path,
    expected_count: int = 40,
) -> list[BenchmarkQuestion]:
    """Load and validate development benchmark questions."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Development benchmark file not found: {file_path}"
        )

    questions = []
    seen_ids = set()

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                question = BenchmarkQuestion.model_validate(record)
            except (json.JSONDecodeError, ValueError) as error:
                raise ValueError(
                    f"Invalid benchmark record on line {line_number}: {error}"
                ) from error

            if question.question_id in seen_ids:
                raise ValueError(
                    f"Duplicate question ID: {question.question_id}"
                )

            seen_ids.add(question.question_id)
            questions.append(question)

    if len(questions) != expected_count:
        raise ValueError(
            f"Expected {expected_count} questions, "
            f"but found {len(questions)}."
        )

    return questions

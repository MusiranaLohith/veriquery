
import json
from datetime import datetime, timezone
from pathlib import Path

from veriquery.llm.client import GenerationResult


class ExperimentRecorder:
    """Append LLM generation attempts to a JSONL experiment file."""

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)


    def load_records(self) -> list[dict]:
        """Load previously recorded experiment attempts."""

        if not self.output_path.exists():
            return []

        records = []

        with self.output_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid experiment record on line {line_number}: {error}"
                    ) from error

        return records


    def completed_question_ids(self) -> set[str]:
        """Return question IDs with at least one successful attempt."""

        records = self.load_records()

        return {
            record["question_id"]
            for record in records
            if record.get("api_status") == "success"
        }

    def attempted_question_ids(self) -> set[str]:
        """Return question IDs that have at least one recorded attempt."""
        records = self.load_records()

        return {
            record["question_id"]
            for record in records
        }

    def record(
        self,
        question_id: str,
        prompt_version: str,
        result: GenerationResult,
    ) -> None:
        """Append one generation attempt as a JSON object."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "question_id": question_id,
            "prompt_version": prompt_version,
            "model_id": result.model_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_seconds": result.latency_seconds,
            "prompt_tokens": result.prompt_tokens,
            "candidate_tokens": result.candidate_tokens,
            "total_tokens": result.total_tokens,
            "api_status": result.api_status,
            "error": result.error,
            "output": (
                result.output.model_dump(mode="json")
                if result.output is not None
                else None
            ),
        }

        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def test_attempted_question_ids_includes_successful_and_failed_attempts(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    success_result = create_success_result()
    failure_result = create_failure_result()

    recorder.record("DEV001", "baseline-v1", success_result)
    recorder.record("DEV002", "baseline-v1", failure_result)

    assert recorder.attempted_question_ids() == {"DEV001", "DEV002"}

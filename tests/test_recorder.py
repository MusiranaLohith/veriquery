
import json

from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.client import GenerationResult
from veriquery.llm.models import SQLGenerationResponse


def create_success_result():
    output = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) AS transaction_count FROM retail_transactions;",
        interpretation="Count transaction records.",
        assumptions=[],
        needs_clarification=False,
    )

    return GenerationResult(
        output=output,
        model_id="test-model",
        latency_seconds=1.25,
        prompt_tokens=100,
        candidate_tokens=50,
        total_tokens=150,
        api_status="success",
        finish_reason="stop",
    )


def create_failure_result():
    return GenerationResult(
        output=None,
        model_id="test-model",
        latency_seconds=2.5,
        prompt_tokens=None,
        candidate_tokens=None,
        total_tokens=None,
        api_status="failed",
        error="RuntimeError: Simulated API failure",
    )


def test_record_success(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    recorder.record("DEV001", "baseline-v1", create_success_result())

    records = [
        json.loads(line)
        for line in (tmp_path / "results.jsonl").read_text().splitlines()
    ]

    assert len(records) == 1
    assert records[0]["question_id"] == "DEV001"
    assert records[0]["api_status"] == "success"
    assert records[0]["output"]["sql"].startswith("SELECT")
    assert records[0]["total_tokens"] == 150
    assert records[0]["finish_reason"] == "stop"


def test_record_failure(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    recorder.record("DEV002", "baseline-v1", create_failure_result())

    records = [
        json.loads(line)
        for line in (tmp_path / "results.jsonl").read_text().splitlines()
    ]

    assert len(records) == 1
    assert records[0]["api_status"] == "failed"
    assert records[0]["output"] is None
    assert "Simulated API failure" in records[0]["error"]


def test_recorder_appends_without_overwriting(tmp_path):
    output_path = tmp_path / "results.jsonl"
    recorder = ExperimentRecorder(output_path)

    recorder.record("DEV001", "baseline-v1", create_success_result())
    recorder.record("DEV002", "baseline-v1", create_failure_result())

    records = [
        json.loads(line)
        for line in output_path.read_text().splitlines()
    ]

    assert len(records) == 2
    assert records[0]["question_id"] == "DEV001"
    assert records[1]["question_id"] == "DEV002"


def test_recorder_creates_parent_directories(tmp_path):
    output_path = tmp_path / "nested" / "experiments" / "results.jsonl"
    recorder = ExperimentRecorder(output_path)

    recorder.record("DEV001", "baseline-v1", create_success_result())

    assert output_path.exists()



def test_load_records_reads_existing_records(tmp_path):
    output_path = tmp_path / "results.jsonl"
    recorder = ExperimentRecorder(output_path)

    recorder.record("DEV001", "baseline-v1", create_success_result())
    recorder.record("DEV002", "baseline-v1", create_failure_result())

    records = recorder.load_records()

    assert len(records) == 2
    assert records[0]["question_id"] == "DEV001"
    assert records[1]["question_id"] == "DEV002"


def test_load_records_returns_empty_list_when_file_missing(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "missing.jsonl")

    assert recorder.load_records() == []


def test_load_records_rejects_malformed_json(tmp_path):
    output_path = tmp_path / "results.jsonl"
    output_path.write_text('{"question_id": "DEV001"\n', encoding="utf-8")

    recorder = ExperimentRecorder(output_path)

    import pytest

    with pytest.raises(ValueError, match="Invalid experiment record on line 1"):
        recorder.load_records()


def test_completed_question_ids_returns_only_successful_questions(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    recorder.record("DEV001", "baseline-v1", create_success_result())
    recorder.record("DEV002", "baseline-v1", create_failure_result())
    recorder.record("DEV003", "baseline-v1", create_success_result())

    assert recorder.completed_question_ids() == {"DEV001", "DEV003"}


def test_attempted_question_ids_includes_successful_and_failed_attempts(tmp_path):
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    success_result = create_success_result()
    failure_result = create_failure_result()

    recorder.record("DEV001", "baseline-v1", success_result)
    recorder.record("DEV002", "baseline-v1", failure_result)

    assert recorder.attempted_question_ids() == {"DEV001", "DEV002"}




def test_record_includes_provider_and_experiment_metadata(tmp_path):
    recorder = ExperimentRecorder(
        tmp_path / "results.jsonl",
        provider="groq",
        experiment_id="full-schema-baseline",
    )

    recorder.record(
        "DEV001",
        "full-schema-baseline-v1",
        create_success_result(),
    )

    records = recorder.load_records()
    record = records[0]

    assert record["provider"] == "groq"
    assert record["experiment_id"] == "full-schema-baseline"
    assert record["question_id"] == "DEV001"
    assert record["model_id"] == "test-model"

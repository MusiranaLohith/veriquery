import pytest
from veriquery.benchmark.models import BenchmarkQuestion
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.client import GenerationResult
from veriquery.llm.models import SQLGenerationResponse

from veriquery.benchmark.runner import (
    BenchmarkRunConfig,
    select_questions,
    select_pending_questions,
    prepare_benchmark_run,
)

def test_default_config_selects_all_questions():
    config = BenchmarkRunConfig()

    assert config.question_ids is None
    assert config.retry_failed is False


def test_config_accepts_selected_dev_questions():
    config = BenchmarkRunConfig(
        question_ids=("DEV001", "DEV005")
    )

    assert config.question_ids == ("DEV001", "DEV005")


def test_config_rejects_empty_question_selection():
    with pytest.raises(ValueError, match="cannot be an empty tuple"):
        BenchmarkRunConfig(question_ids=())


def test_config_rejects_duplicate_question_ids():
    with pytest.raises(ValueError, match="cannot contain duplicates"):
        BenchmarkRunConfig(
            question_ids=("DEV001", "DEV001")
        )


def test_config_rejects_non_dev_question_ids():
    with pytest.raises(ValueError, match="Only development"):
        BenchmarkRunConfig(
            question_ids=("TEST001",)
        )


def test_config_allows_retrying_failed_attempts():
    config = BenchmarkRunConfig(
        question_ids=("DEV001",),
        retry_failed=True,
    )

    assert config.retry_failed is True



def create_question(question_id):
    return BenchmarkQuestion(
        question_id=question_id,
        question=f"Question {question_id}?",
        category="schema_understanding",
        difficulty="easy",
        answerability="answerable",
    )


def create_success_result():
    output = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) FROM retail_transactions;",
        interpretation="Count transactions.",
        assumptions=[],
        needs_clarification=False,
    )

    return GenerationResult(
        output=output,
        model_id="test-model",
        latency_seconds=1.0,
        prompt_tokens=100,
        candidate_tokens=50,
        total_tokens=150,
        api_status="success",
        error=None,
    )


def create_failure_result():
    return GenerationResult(
        output=None,
        model_id="test-model",
        latency_seconds=1.0,
        prompt_tokens=None,
        candidate_tokens=None,
        total_tokens=None,
        api_status="failed",
        error="Simulated API failure",
    )


def test_select_all_questions_by_default():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
    ]

    selected = select_questions(questions, BenchmarkRunConfig())

    assert len(selected) == 2
    assert selected == questions


def test_select_specific_questions():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    config = BenchmarkRunConfig(
        question_ids=("DEV001", "DEV003")
    )

    selected = select_questions(questions, config)

    assert [q.question_id for q in selected] == ["DEV001", "DEV003"]


def test_selection_preserves_benchmark_order():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    config = BenchmarkRunConfig(
        question_ids=("DEV003", "DEV001")
    )

    selected = select_questions(questions, config)

    assert [q.question_id for q in selected] == ["DEV001", "DEV003"]


def test_selection_rejects_unknown_question_ids():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
    ]

    config = BenchmarkRunConfig(question_ids=("DEV040",))

    with pytest.raises(ValueError, match="Unknown development"):
        select_questions(questions, config)



def test_pending_questions_skip_failed_attempts_by_default():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    pending = select_pending_questions(
        questions,
        attempted_ids={"DEV001", "DEV002"},
        completed_ids={"DEV002"},
        config=BenchmarkRunConfig(),
    )

    assert [q.question_id for q in pending] == ["DEV003"]


def test_pending_questions_retry_failed_attempts_when_enabled():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    pending = select_pending_questions(
        questions,
        attempted_ids={"DEV001", "DEV002"},
        completed_ids={"DEV002"},
        config=BenchmarkRunConfig(retry_failed=True),
    )

    assert [q.question_id for q in pending] == ["DEV001", "DEV003"]


def test_pending_questions_respect_selected_ids():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    pending = select_pending_questions(
        questions,
        attempted_ids={"DEV001"},
        completed_ids={"DEV001"},
        config=BenchmarkRunConfig(
            question_ids=("DEV001", "DEV003"),
            retry_failed=True,
        ),
    )

    assert [q.question_id for q in pending] == ["DEV003"]


def test_pending_questions_return_empty_when_all_completed():
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
    ]

    pending = select_pending_questions(
        questions,
        attempted_ids={"DEV001", "DEV002"},
        completed_ids={"DEV001", "DEV002"},
        config=BenchmarkRunConfig(),
    )

    assert pending == []



def test_prepare_benchmark_run_uses_recorder_history(tmp_path):
    questions = [
        create_question("DEV001"),
        create_question("DEV002"),
        create_question("DEV003"),
    ]

    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    recorder.record("DEV001", "baseline-v1", create_success_result())
    recorder.record("DEV002", "baseline-v1", create_failure_result())

    pending = prepare_benchmark_run(
        questions=questions,
        recorder=recorder,
        config=BenchmarkRunConfig(),
    )

    assert [q.question_id for q in pending] == ["DEV003"]

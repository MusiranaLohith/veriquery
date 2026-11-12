
import json

from veriquery.benchmark.executor import BenchmarkExecutor
from veriquery.benchmark.models import BenchmarkQuestion
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.client import GenerationResult
from veriquery.llm.models import SQLGenerationResponse


class FakeGeminiClient:
    """Mock Gemini client that never makes real API requests."""

    def __init__(self, results):
        self.results = iter(results)
        self.received_prompts = []

    def generate(self, prompt):
        self.received_prompts.append(prompt)
        return next(self.results)


def create_question(question_id, question_text):
    return BenchmarkQuestion(
        question_id=question_id,
        question=question_text,
        category="schema_understanding",
        difficulty="easy",
        answerability="answerable",
    )


def create_success_result():
    output = SQLGenerationResponse(
        is_answerable=True,
        sql="SELECT COUNT(*) FROM retail_transactions;",
        interpretation="Count transaction records.",
        assumptions=[],
        needs_clarification=False,
    )

    return GenerationResult(
        output=output,
        model_id="fake-model",
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
        model_id="fake-model",
        latency_seconds=1.0,
        prompt_tokens=None,
        candidate_tokens=None,
        total_tokens=None,
        api_status="failed",
        error="Simulated API failure",
    )


def test_executor_records_successful_and_failed_results(tmp_path):
    questions = [
        create_question("DEV001", "Count all transaction records."),
        create_question("DEV002", "Count distinct customers."),
    ]

    fake_client = FakeGeminiClient([
        create_success_result(),
        create_failure_result(),
    ])

    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    executor = BenchmarkExecutor(
        client=fake_client,
        recorder=recorder,
    )

    summary = executor.execute(questions)

    assert summary.total_questions == 2
    assert summary.successful == 1
    assert summary.failed == 1
    assert summary.skipped == 0

    records = recorder.load_records()

    assert len(records) == 2
    assert records[0]["question_id"] == "DEV001"
    assert records[0]["api_status"] == "success"
    assert records[1]["question_id"] == "DEV002"
    assert records[1]["api_status"] == "failed"


def test_executor_builds_prompt_for_each_question(tmp_path):
    questions = [
        create_question("DEV001", "Count all transaction records."),
        create_question("DEV002", "Count distinct customers."),
    ]

    fake_client = FakeGeminiClient([
        create_success_result(),
        create_success_result(),
    ])

    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    executor = BenchmarkExecutor(fake_client, recorder)

    executor.execute(questions)

    assert len(fake_client.received_prompts) == 2

    assert "Count all transaction records." in fake_client.received_prompts[0]
    assert "Count distinct customers." in fake_client.received_prompts[1]


def test_executor_handles_empty_question_list(tmp_path):
    fake_client = FakeGeminiClient([])
    recorder = ExperimentRecorder(tmp_path / "results.jsonl")

    executor = BenchmarkExecutor(fake_client, recorder)

    summary = executor.execute([])

    assert summary.total_questions == 0
    assert summary.successful == 0
    assert summary.failed == 0
    assert summary.skipped == 0
    assert fake_client.received_prompts == []

    assert not recorder.output_path.exists()


def test_executor_preserves_every_attempt_in_jsonl(tmp_path):
    questions = [
        create_question("DEV001", "Question one."),
        create_question("DEV002", "Question two."),
        create_question("DEV003", "Question three."),
    ]

    fake_client = FakeGeminiClient([
        create_failure_result(),
        create_success_result(),
        create_failure_result(),
    ])

    output_path = tmp_path / "results.jsonl"
    recorder = ExperimentRecorder(output_path)

    executor = BenchmarkExecutor(fake_client, recorder)

    summary = executor.execute(questions)

    raw_lines = output_path.read_text(encoding="utf-8").splitlines()

    assert len(raw_lines) == 3
    assert all(isinstance(json.loads(line), dict) for line in raw_lines)

    assert summary.total_questions == 3
    assert summary.successful == 1
    assert summary.failed == 2

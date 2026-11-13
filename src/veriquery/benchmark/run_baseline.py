
import argparse
from pathlib import Path

from veriquery.benchmark.loader import load_dev_questions
from veriquery.benchmark.runner import (
    BenchmarkRunConfig,
    prepare_benchmark_run,
)
from veriquery.benchmark.executor import BenchmarkExecutor
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.prompts import PROMPT_VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEV_QUESTIONS_PATH = (
    PROJECT_ROOT / "data" / "benchmark" / "dev" / "dev_questions.jsonl"
)

RESULTS_PATHS = {
    "gemini": (
        PROJECT_ROOT
        / "experiments"
        / "results"
        / "gemini_full_schema_baseline_v3.jsonl"
    ),
    "groq": (
        PROJECT_ROOT
        / "experiments"
        / "results"
        / "groq_full_schema_baseline_v3.jsonl"
    ),
}

EXPERIMENT_ID = "full-schema-json-object-v3"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the VeriQuery full-schema development baseline."
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "groq"],
        default="gemini",
        help="LLM provider for this experiment.",
    )

    parser.add_argument(
        "--results-path",
        type=Path,
        default=None,
        help="Optional explicit path for this experiment's JSONL results.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare the benchmark without making API calls.",
    )

    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry previously failed questions.",
    )

    return parser.parse_args()


def create_client(provider: str):
    """Create the selected provider client."""

    if provider == "gemini":
        from veriquery.llm.client import GeminiSQLClient
        return GeminiSQLClient()

    if provider == "groq":
        from veriquery.llm.groq_client import GroqSQLClient
        return GroqSQLClient()

    raise ValueError(f"Unsupported provider: {provider}")


def validate_existing_experiment(recorder: ExperimentRecorder):
    """Prevent mixing records from different experiments."""

    for record in recorder.load_records():
        if record.get("experiment_id") != EXPERIMENT_ID:
            raise ValueError(
                "Results file contains records from another experiment. "
                f"Expected {EXPERIMENT_ID!r}, got "
                f"{record.get('experiment_id')!r}."
            )

        if record.get("provider") != recorder.provider:
            raise ValueError(
                "Results file contains records from another provider."
            )

        if record.get("prompt_version") != PROMPT_VERSION:
            raise ValueError(
                "Results file contains records from another prompt version. "
                f"Expected {PROMPT_VERSION!r}, got "
                f"{record.get('prompt_version')!r}."
            )


def main():
    args = parse_args()

    print("\n=== VeriQuery Full-Schema Baseline ===\n")
    print(f"Provider: {args.provider}")
    print(f"Experiment: {EXPERIMENT_ID}")
    print(f"Prompt version: {PROMPT_VERSION}")

    questions = load_dev_questions(
        DEV_QUESTIONS_PATH,
        expected_count=40,
    )

    print(f"Development questions loaded: {len(questions)}")

    results_path = (
        args.results_path
        if args.results_path is not None
        else RESULTS_PATHS[args.provider]
    )

    recorder = ExperimentRecorder(
        output_path=results_path,
        provider=args.provider,
        experiment_id=EXPERIMENT_ID,
    )

    validate_existing_experiment(recorder)

    config = BenchmarkRunConfig(
        retry_failed=args.retry_failed,
    )

    pending_questions = prepare_benchmark_run(
        questions=questions,
        recorder=recorder,
        config=config,
    )

    print(f"Previously attempted: {len(recorder.attempted_question_ids())}")
    print(f"Previously completed: {len(recorder.completed_question_ids())}")
    print(f"Pending questions: {len(pending_questions)}")

    print(f"Results file: {results_path}")

    if args.dry_run:
        print("\nDRY RUN COMPLETE")
        print("No API requests were made.")
        return

    if not pending_questions:
        print("\nNo pending questions. Nothing to execute.")
        return

    client = create_client(args.provider)

    request_interval_seconds = 45 if args.provider == "groq" else 0

    executor = BenchmarkExecutor(
        client=client,
        recorder=recorder,
        request_interval_seconds=request_interval_seconds,
    )

    summary = executor.execute(pending_questions)

    print("\n=== Run Summary ===")
    print(f"Provider: {args.provider}")
    print(f"Processed: {summary.total_questions}")
    print(f"Successful: {summary.successful}")
    print(f"Failed: {summary.failed}")
    print(f"Skipped: {summary.skipped}")
    print(f"Results saved to: {results_path}")


if __name__ == "__main__":
    main()

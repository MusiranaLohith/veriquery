
import argparse
from pathlib import Path

from veriquery.benchmark.loader import load_dev_questions
from veriquery.benchmark.runner import (
    BenchmarkRunConfig,
    prepare_benchmark_run,
)
from veriquery.benchmark.executor import (
    BenchmarkExecutor,
    BenchmarkRunSummary,
)
from veriquery.experiments.recorder import ExperimentRecorder


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEV_QUESTIONS_PATH = (
    PROJECT_ROOT / "data" / "benchmark" / "dev" / "dev_questions.jsonl"
)

RESULTS_PATHS = {
    "gemini": PROJECT_ROOT / "experiments" / "results" / "full_schema_baseline.jsonl",
    "groq": PROJECT_ROOT / "experiments" / "results" / "groq_full_schema_baseline.jsonl",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the VeriQuery full-schema development baseline."
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "groq"],
        default="gemini",
        help="LLM provider for this experiment (default: gemini).",
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


def main():
    args = parse_args()

    print("\n=== VeriQuery Full-Schema Baseline ===\n")
    print(f"Provider: {args.provider}")

    questions = load_dev_questions(
        DEV_QUESTIONS_PATH,
        expected_count=40,
    )

    print(f"Development questions loaded: {len(questions)}")

    results_path = RESULTS_PATHS[args.provider]

    recorder = ExperimentRecorder(
        output_path=results_path,
        provider=args.provider,
        experiment_id="full-schema-baseline",
    )

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

    if args.dry_run:
        print("\nDRY RUN COMPLETE")
        print("No API requests were made.")
        print(f"Experiment results file: {results_path}")
        return

    if not pending_questions:
        print("\nNo pending questions. Nothing to execute.")
        return

    client = create_client(args.provider)

    executor = BenchmarkExecutor(
        client=client,
        recorder=recorder,
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

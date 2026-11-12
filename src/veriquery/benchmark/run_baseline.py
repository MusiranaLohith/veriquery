
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
from veriquery.llm.client import GeminiSQLClient


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEV_QUESTIONS_PATH = (
    PROJECT_ROOT / "data" / "benchmark" / "dev" / "dev_questions.jsonl"
)

RESULTS_PATH = (
    PROJECT_ROOT / "experiments" / "results" / "full_schema_baseline.jsonl"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the VeriQuery full-schema development baseline."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare the benchmark without making Gemini API calls.",
    )

    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry previously failed questions.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    print("\n=== VeriQuery Full-Schema Baseline ===\n")

    # 1. Load development questions only.
    questions = load_dev_questions(
        DEV_QUESTIONS_PATH,
        expected_count=40,
    )

    print(f"Development questions loaded: {len(questions)}")

    # 2. Load experiment history.
    recorder = ExperimentRecorder(RESULTS_PATH)

    # 3. Apply the retry/resume policy.
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

    # 4. Dry-run: stop before initializing or calling Gemini.
    if args.dry_run:
        print("\nDRY RUN COMPLETE")
        print("No Gemini API requests were made.")
        return

    if not pending_questions:
        print("\nNo pending questions. Nothing to execute.")
        return

    # 5. Execute pending questions.
    client = GeminiSQLClient()

    executor = BenchmarkExecutor(
        client=client,
        recorder=recorder,
    )

    summary = executor.execute(pending_questions)

    # 6. Display this run's results.
    print("\n=== Run Summary ===")
    print(f"Processed: {summary.total_questions}")
    print(f"Successful: {summary.successful}")
    print(f"Failed: {summary.failed}")
    print(f"Skipped: {summary.skipped}")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()

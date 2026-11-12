
from pathlib import Path

from veriquery.benchmark.loader import load_dev_questions
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.groq_client import GroqSQLClient
from veriquery.llm.prompts import build_prompt, PROMPT_VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEV_QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "benchmark"
    / "dev"
    / "dev_questions.jsonl"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "results"
    / "groq_smoke_test.jsonl"
)

SMOKE_QUESTION_ID = "DEV001"


def main():
    print("\n=== VeriQuery Groq Smoke Test ===\n")

    # 1. Load development questions only.
    questions = load_dev_questions(
        DEV_QUESTIONS_PATH,
        expected_count=40,
    )

    # 2. Select exactly one question.
    matches = [
        question
        for question in questions
        if question.question_id == SMOKE_QUESTION_ID
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {SMOKE_QUESTION_ID} question."
        )

    question = matches[0]

    print(f"Question ID: {question.question_id}")
    print(f"Question: {question.question}")

    # 3. Use the existing full-schema prompt.
    prompt = build_prompt(question.question)

    # 4. Prepare a separate Groq experiment recorder.
    recorder = ExperimentRecorder(RESULTS_PATH)

    # Prevent accidental duplicate smoke-test requests.
    existing_records = recorder.load_records()

    if any(
        record.get("question_id") == SMOKE_QUESTION_ID
        for record in existing_records
    ):
        print("\nSmoke test already recorded.")
        print("No API request will be made.")
        return

    # 5. Initialize Groq only after all local checks pass.
    client = GroqSQLClient()

    print("\nSending exactly one request to Groq...")
    result = client.generate(prompt)

    # 6. Preserve the result, including failures.
    recorder.record(
        question_id=question.question_id,
        prompt_version=f"groq-{PROMPT_VERSION}",
        result=result,
    )

    # 7. Display the outcome.
    print("\n=== Smoke Test Result ===")
    print(f"Model: {result.model_id}")
    print(f"Status: {result.api_status}")
    print(f"Latency: {result.latency_seconds:.2f} seconds")
    print(f"Prompt tokens: {result.prompt_tokens}")
    print(f"Completion tokens: {result.candidate_tokens}")
    print(f"Total tokens: {result.total_tokens}")

    if result.output is None:
        print(f"Error: {result.error}")
        print("\nNo valid structured response was generated.")
    else:
        print("\nStructured response:")
        print(result.output.model_dump_json(indent=2))

    print(f"\nExperiment saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()

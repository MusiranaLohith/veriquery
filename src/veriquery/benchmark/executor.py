
from dataclasses import dataclass

from veriquery.benchmark.models import BenchmarkQuestion
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.client import GeminiSQLClient
from veriquery.llm.prompts import build_prompt, PROMPT_VERSION


@dataclass
class BenchmarkRunSummary:
    """Summary of a development benchmark execution."""

    total_questions: int
    successful: int
    failed: int
    skipped: int


class BenchmarkExecutor:
    """Execute development benchmark questions using the full-schema baseline."""

    def __init__(
        self,
        client: GeminiSQLClient,
        recorder: ExperimentRecorder,
    ):
        self.client = client
        self.recorder = recorder

    def execute(
        self,
        questions: list[BenchmarkQuestion],
    ) -> BenchmarkRunSummary:
        """Generate and record one result for every supplied question."""

        successful = 0
        failed = 0

        for index, question in enumerate(questions, start=1):
            print(
                f"[{index}/{len(questions)}] "
                f"Processing {question.question_id}..."
            )

            prompt = build_prompt(question.question)

            result = self.client.generate(prompt)

            self.recorder.record(
                question_id=question.question_id,
                prompt_version=PROMPT_VERSION,
                result=result,
            )

            if result.output is not None and result.api_status == "success":
                successful += 1
                print(f"  SUCCESS: {question.question_id}")
            else:
                failed += 1
                print(
                    f"  FAILED: {question.question_id} "
                    f"({result.api_status})"
                )

        return BenchmarkRunSummary(
            total_questions=len(questions),
            successful=successful,
            failed=failed,
            skipped=0,
        )

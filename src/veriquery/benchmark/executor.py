
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Protocol

from veriquery.benchmark.models import BenchmarkQuestion
from veriquery.experiments.recorder import ExperimentRecorder
from veriquery.llm.client import GenerationResult
from veriquery.llm.prompts import build_prompt, PROMPT_VERSION


class SQLGenerationClient(Protocol):
    """Interface shared by all SQL generation providers."""

    def generate(self, prompt: str) -> GenerationResult:
        ...


@dataclass
class BenchmarkRunSummary:
    """Summary of a development benchmark execution."""

    total_questions: int
    successful: int
    failed: int
    skipped: int


def get_retry_after_seconds(result: GenerationResult) -> float:
    """Extract a wait duration from the Retry-After response header."""

    headers = result.rate_limit_headers or {}
    retry_after = headers.get("retry-after")

    if not retry_after:
        return 0.0

    try:
        return max(0.0, float(retry_after))
    except (TypeError, ValueError):
        pass

    try:
        retry_date = parsedate_to_datetime(retry_after)

        if retry_date.tzinfo is None:
            retry_date = retry_date.replace(tzinfo=timezone.utc)

        remaining_seconds = (
            retry_date - datetime.now(timezone.utc)
        ).total_seconds()

        return max(0.0, remaining_seconds)

    except (TypeError, ValueError, OverflowError):
        return 0.0


class BenchmarkExecutor:
    """Execute the full-schema baseline using any compatible LLM client."""

    def __init__(
        self,
        client: SQLGenerationClient,
        recorder: ExperimentRecorder,
        request_interval_seconds: float = 0,
    ):
        if request_interval_seconds < 0:
            raise ValueError("Request interval cannot be negative.")

        self.client = client
        self.recorder = recorder
        self.request_interval_seconds = request_interval_seconds

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

            if index < len(questions):
                retry_after_seconds = 0.0

                if result.api_status == "rate_limited":
                    retry_after_seconds = get_retry_after_seconds(result)

                wait_seconds = max(
                    self.request_interval_seconds,
                    retry_after_seconds,
                )

                if wait_seconds > 0:
                    print(
                        f"  Waiting {wait_seconds:g} seconds "
                        "before the next request..."
                    )
                    time.sleep(wait_seconds)

        return BenchmarkRunSummary(
            total_questions=len(questions),
            successful=successful,
            failed=failed,
            skipped=0,
        )

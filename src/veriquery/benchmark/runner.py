
from dataclasses import dataclass

from veriquery.benchmark.models import BenchmarkQuestion
from veriquery.experiments.recorder import ExperimentRecorder

@dataclass(frozen=True)
class BenchmarkRunConfig:
    """Controls which development benchmark questions may run."""

    question_ids: tuple[str, ...] | None = None
    retry_failed: bool = False

    def __post_init__(self):
        if self.question_ids is not None:
            if not self.question_ids:
                raise ValueError(
                    "question_ids cannot be an empty tuple."
                )

            if len(set(self.question_ids)) != len(self.question_ids):
                raise ValueError(
                    "question_ids cannot contain duplicates."
                )

            for question_id in self.question_ids:
                if not question_id.startswith("DEV"):
                    raise ValueError(
                        "Only development question IDs are allowed."
                    )


def select_questions(
    questions: list[BenchmarkQuestion],
    config: BenchmarkRunConfig,
) -> list[BenchmarkQuestion]:
    """Select development questions according to the run configuration."""

    available_ids = {question.question_id for question in questions}

    if config.question_ids is None:
        return questions.copy()

    requested_ids = set(config.question_ids)

    unknown_ids = requested_ids - available_ids

    if unknown_ids:
        raise ValueError(
            f"Unknown development question IDs: {sorted(unknown_ids)}"
        )

    return [
        question
        for question in questions
        if question.question_id in requested_ids
    ]




def select_pending_questions(
    questions: list[BenchmarkQuestion],
    attempted_ids: set[str],
    completed_ids: set[str],
    config: BenchmarkRunConfig,
) -> list[BenchmarkQuestion]:
    """Select questions eligible to run under the retry policy."""
    selected_questions = select_questions(questions, config)

    if config.retry_failed:
        excluded_ids = completed_ids
    else:
        excluded_ids = attempted_ids

    return [
        question
        for question in selected_questions
        if question.question_id not in excluded_ids
    ]



def prepare_benchmark_run(
    questions: list[BenchmarkQuestion],
    recorder: ExperimentRecorder,
    config: BenchmarkRunConfig,
) -> list[BenchmarkQuestion]:
    """Prepare development questions by applying the experiment resume policy."""
    attempted_ids = recorder.attempted_question_ids()
    completed_ids = recorder.completed_question_ids()

    return select_pending_questions(
        questions=questions,
        attempted_ids=attempted_ids,
        completed_ids=completed_ids,
        config=config,
    )

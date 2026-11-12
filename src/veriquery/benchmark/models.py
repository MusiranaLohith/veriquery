
from typing import Literal

from pydantic import BaseModel, Field


class BenchmarkQuestion(BaseModel):
    """Validated representation of one development benchmark question."""

    question_id: str = Field(pattern=r"^DEV\d{3}$")
    question: str = Field(min_length=1)
    category: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    answerability: Literal["answerable", "unanswerable"]

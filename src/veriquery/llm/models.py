
from pydantic import BaseModel, Field, model_validator


class SQLGenerationResponse(BaseModel):
    """Structured response produced by the LLM."""

    is_answerable: bool = Field(
        description="Whether the database schema can answer the question."
    )

    sql: str | None = Field(
        description="Generated PostgreSQL SELECT query, or null."
    )

    interpretation: str = Field(
        description="Brief interpretation of the user's question."
    )

    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made during SQL generation."
    )

    needs_clarification: bool = Field(
        description="Whether clarification is required."
    )

    @model_validator(mode="after")
    def validate_answerability(self):
        """Enforce consistency between answerability, clarification and SQL."""

        if not self.is_answerable and self.sql is not None:
            raise ValueError(
                "Unanswerable questions must not contain SQL."
            )

        if self.needs_clarification and self.sql is not None:
            raise ValueError(
                "Responses requiring clarification must not contain SQL."
            )

        if self.is_answerable and not self.needs_clarification:
            if not self.sql or not self.sql.strip():
                raise ValueError(
                    "Answerable responses without clarification require non-empty SQL."
                )

        return self

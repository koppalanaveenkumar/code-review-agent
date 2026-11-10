from typing import Literal

from pydantic import BaseModel, Field


class ReviewComment(BaseModel):
    file: str
    line: int = Field(ge=1)
    severity: Literal["bug", "security"]
    problem: str
    example: str
    fix: str


class ReviewResult(BaseModel):
    comments: list[ReviewComment]
    
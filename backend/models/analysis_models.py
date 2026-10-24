from pydantic import BaseModel, Field
from typing import Literal

class AnalyzeCodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100_000)


class CodeIssue(BaseModel):
    line: int
    category: Literal[
        "security",
        "maintainability",
        "syntax"
    ]
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical"
    ]
    description: str

class AnalysisResponse(BaseModel):
    language: str
    issues_count: int
    issues: list[CodeIssue]
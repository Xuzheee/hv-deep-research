from pydantic import BaseModel, Field


class QualityCheckResult(BaseModel):
    quality_warning: bool = False
    quality_issues: list[str] = Field(default_factory=list)
    quality_score: int = Field(ge=0, le=100)
    source_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)

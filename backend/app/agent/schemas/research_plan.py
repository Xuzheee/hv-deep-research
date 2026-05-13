from pydantic import BaseModel, Field

from app.agent.schemas.report import SubjectType
from app.agent.schemas.source import Dimension


class PlannedQuery(BaseModel):
    query: str
    intended_dimension: Dimension


class ResearchPlan(BaseModel):
    subject: str
    subject_type: SubjectType
    research_motivation: str | None = None
    vertical_questions: list[str]
    horizontal_questions: list[str]
    supplementary_questions: list[str] = Field(default_factory=list)
    initial_queries: list[str]
    planned_queries: list[PlannedQuery] = Field(default_factory=list)
    expected_competitors: list[str] = Field(default_factory=list)
    source_preferences: list[str] = Field(default_factory=list)

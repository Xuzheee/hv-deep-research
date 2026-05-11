from typing import Literal

from pydantic import BaseModel, Field

from app.agent.schemas.evidence import EvidenceGroup, KeyFinding, RiskNote
from app.agent.schemas.source import ConfidenceLevel


class NarrativeSection(BaseModel):
    section_id: str
    title: str
    content: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)


class FutureScenarios(BaseModel):
    most_likely: str
    most_dangerous: str
    most_optimistic: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)


class NarrativeReportData(BaseModel):
    title: str
    one_sentence_definition: str
    opening_judgment: str
    vertical_story: list[NarrativeSection] = Field(default_factory=list)
    horizontal_comparison: list[NarrativeSection] = Field(default_factory=list)
    intersection_insights: list[NarrativeSection] = Field(default_factory=list)
    future_scenarios: FutureScenarios
    source_notes: list[str] = Field(default_factory=list)

SubjectType = Literal["product", "company", "concept", "person", "technology", "other"]
UpdateType = Literal[
    "product_launch",
    "feature_update",
    "pricing_change",
    "partnership",
    "policy_change",
    "other",
]
BoundaryType = Literal[
    "short_term_feature",
    "long_term_moat",
    "current_weakness",
    "emerging_threat",
]
Priority = Literal["high", "medium", "low"]


class ReleaseUpdate(BaseModel):
    update_id: str
    date: str | None = None
    title: str
    content: str
    update_type: UpdateType
    source_url: str | None = None
    confidence: ConfidenceLevel = "medium"


class OverviewTabData(BaseModel):
    product_overview: str
    release_updates: list[ReleaseUpdate] = Field(default_factory=list)
    key_findings: list[KeyFinding] = Field(default_factory=list)
    evidence_groups: list[EvidenceGroup] = Field(default_factory=list)
    risk_notes: list[RiskNote] = Field(default_factory=list)


class VerticalStage(BaseModel):
    stage_id: str
    stage_number: int
    title: str
    period: str | None = None
    summary: str
    key_events: list[str] = Field(default_factory=list)
    driving_forces: list[str] = Field(default_factory=list)
    path_dependencies: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str]


class VerticalTabData(BaseModel):
    full_text: str
    stages: list[VerticalStage] = Field(default_factory=list)
    key_turning_points: list[str] = Field(default_factory=list)
    path_dependency_summary: str


class CompetitorMatrixItem(BaseModel):
    competitor_id: str
    name: str
    role: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    best_for: str
    pricing_or_access: str | None = None
    supporting_evidence_ids: list[str]


class CapabilityBoundary(BaseModel):
    boundary_id: str
    title: str
    description: str
    boundary_type: BoundaryType
    supporting_evidence_ids: list[str]


class Recommendation(BaseModel):
    rec_id: str
    title: str
    content: str
    priority: Priority
    target_audience: str | None = None
    rationale: str
    supporting_evidence_ids: list[str]


class HorizontalTabData(BaseModel):
    full_text: str
    competitor_scenario: Literal["no_direct_competitor", "few_competitors", "mature_market"]
    competitor_matrix: list[CompetitorMatrixItem] = Field(default_factory=list)
    capability_boundaries: list[CapabilityBoundary] = Field(default_factory=list)
    positioning_summary: str
    recommendations: list[Recommendation] = Field(default_factory=list)


class ReportData(BaseModel):
    report_id: str
    topic: str
    subject: str
    subject_type: SubjectType
    title: str
    subtitle: str | None = None
    overview: OverviewTabData
    vertical: VerticalTabData
    horizontal: HorizontalTabData
    narrative_report: NarrativeReportData | None = None
    quality_warning: bool = False
    quality_issues: list[str] = Field(default_factory=list)
    quality_score: int = Field(ge=0, le=100)
    source_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    generated_at: str
    limitations: list[str] = Field(default_factory=list)

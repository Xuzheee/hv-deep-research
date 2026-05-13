from typing import TypedDict

from app.agent.schemas.evidence import EvidenceCard, EvidenceGroup
from app.agent.schemas.quality import QualityCheckResult
from app.agent.schemas.report import CrossInsight, HorizontalTabData, ReportData, SubjectType, VerticalTabData
from app.agent.schemas.research_plan import ResearchPlan
from app.agent.schemas.source import CandidateSource, CollectedNote


class ReportAgentState(TypedDict, total=False):
    report_id: str
    topic: str
    subject: str
    subject_type: SubjectType
    status: str
    progress_message: str
    research_plan: ResearchPlan
    candidate_sources: list[CandidateSource]
    collected_notes: list[CollectedNote]
    evidence_cards: list[EvidenceCard]
    evidence_groups: list[EvidenceGroup]
    cross_insights: list[CrossInsight]
    vertical: VerticalTabData
    horizontal: HorizontalTabData
    quality_check: QualityCheckResult
    report_data: ReportData
    report_data_path: str
    evidence_cards_path: str
    raw_sources_path: str
    run_log_path: str
    quality_check_path: str
    artifact_paths: dict[str, str]
    run_log: list[dict]
    tool_call_count: int
    quality_remediation_attempted: bool
    reports_output_dir: str
    error_message: str | None

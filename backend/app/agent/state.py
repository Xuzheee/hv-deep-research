from typing import TypedDict

from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.report import ReportData, SubjectType
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
    report_data: ReportData
    error_message: str | None

from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceGroup, KeyFinding, RiskNote
from app.agent.schemas.report import OverviewTabData, ReleaseUpdate, ReportData
from app.agent.state import ReportAgentState


def synthesis_report_data(state: ReportAgentState) -> ReportAgentState:
    evidence_cards = state["evidence_cards"]
    evidence_ids = [card.evidence_id for card in evidence_cards]
    subject = state["subject"]
    overview = OverviewTabData(
        product_overview=f"{subject} report generated from {len(evidence_cards)} evidence cards.",
        release_updates=[
            ReleaseUpdate(
                update_id="update_001",
                title="MVP research workflow completed",
                content="The backend produced a deterministic report_data payload from ranked and scraped sources.",
                update_type="other",
                source_url=evidence_cards[0].url if evidence_cards else None,
                confidence="medium",
            )
        ],
        key_findings=[
            KeyFinding(
                finding_id="finding_001",
                title="Evidence-backed MVP report generated",
                content=f"The workflow generated structured report data for {subject}.",
                confidence="medium",
                supporting_evidence_ids=evidence_ids[:3],
            )
        ],
        evidence_groups=[
            EvidenceGroup(
                group_id="group_001",
                label="Collected source evidence",
                description="Evidence cards produced from ranked mockable source adapters.",
                source_count=len(state["candidate_sources"]),
                evidence_count=len(evidence_cards),
                dominant_tier="unknown",
                confidence="medium",
                evidence_ids=evidence_ids,
            )
        ],
        risk_notes=[
            RiskNote(
                risk_id="risk_001",
                title="MVP source limitation",
                content="Report content is deterministic and should be re-run with live API keys for production research.",
                severity="low",
                supporting_evidence_ids=evidence_ids[:3],
            )
        ],
    )
    state["report_data"] = ReportData(
        report_id=state["report_id"],
        topic=state["topic"],
        subject=subject,
        subject_type=state["subject_type"],
        title=f"{subject} Deep Research Report",
        subtitle="MVP evidence-backed report",
        overview=overview,
        vertical=state["vertical"],
        horizontal=state["horizontal"],
        quality_warning=False,
        quality_issues=[],
        quality_score=85,
        source_count=len(state["candidate_sources"]),
        evidence_count=len(evidence_cards),
        generated_at=evidence_cards[0].retrieved_at if evidence_cards else "2026-05-08T00:00:00+00:00",
        limitations=["Deterministic MVP output", "Mock adapters are used when API keys are absent"],
    )
    return ProgressReporter().report(state, "quality_checking", "Synthesized frontend-compatible report data.")

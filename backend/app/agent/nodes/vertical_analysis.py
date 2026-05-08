from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.report import VerticalStage, VerticalTabData
from app.agent.state import ReportAgentState


def vertical_analysis(state: ReportAgentState) -> ReportAgentState:
    evidence_ids = [card.evidence_id for card in state["evidence_cards"][:3]]
    subject = state["subject"]
    state["vertical"] = VerticalTabData(
        full_text=f"{subject} is analyzed through the collected evidence cards for this MVP run.",
        stages=[
            VerticalStage(
                stage_id="stage_001",
                stage_number=1,
                title=f"Initial evidence-backed view of {subject}",
                period="MVP baseline",
                summary=f"The current MVP evidence set establishes a baseline narrative for {subject}.",
                key_events=["Initial research workflow completed"],
                driving_forces=["Evidence-driven product research"],
                path_dependencies=["Available ranked sources and scraped notes"],
                supporting_evidence_ids=evidence_ids,
            )
        ],
        key_turning_points=["Evidence collection completed"],
        path_dependency_summary="The MVP narrative depends on ranked sources and deterministic mock adapters when API keys are absent.",
    )
    return ProgressReporter().report(state, "analyzing_horizontal", "Completed vertical analysis.")

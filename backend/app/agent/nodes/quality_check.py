from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.quality import QualityCheckResult
from app.agent.state import ReportAgentState


def quality_check(state: ReportAgentState) -> ReportAgentState:
    report_data = state["report_data"]
    issues = []
    if report_data.evidence_count == 0:
        issues.append("No evidence cards were generated.")
    if report_data.source_count == 0:
        issues.append("No sources were collected.")

    state["quality_check"] = QualityCheckResult(
        quality_warning=bool(issues),
        quality_issues=issues,
        quality_score=max(0, report_data.quality_score - (20 if issues else 0)),
        source_count=report_data.source_count,
        evidence_count=report_data.evidence_count,
    )
    report_data.quality_warning = state["quality_check"].quality_warning
    report_data.quality_issues = state["quality_check"].quality_issues
    report_data.quality_score = state["quality_check"].quality_score
    return ProgressReporter().report(state, "persisting", "Completed report quality check.")

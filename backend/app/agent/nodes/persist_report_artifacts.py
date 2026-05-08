from app.agent.progress_reporter import ProgressReporter
from app.agent.state import ReportAgentState
from app.agent.tools.file_store import ReportFileStore


def persist_report_artifacts(state: ReportAgentState) -> ReportAgentState:
    file_store = ReportFileStore(state.get("reports_output_dir", "backend/app/outputs/reports"))
    state["artifact_paths"] = file_store.write_report_artifacts(
        state["report_id"],
        report_data=state["report_data"],
        evidence_cards=state["evidence_cards"],
        raw_sources=state["collected_notes"],
        run_log=state.get("run_log", []),
        quality_check=state["quality_check"],
    )
    return ProgressReporter().report(state, "completed", "Saved report artifacts.")

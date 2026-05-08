from app.agent.progress_reporter import ProgressReporter
from app.agent.state import ReportAgentState


def initialize_report_run(state: ReportAgentState) -> ReportAgentState:
    state["subject"] = state.get("subject") or state["topic"]
    state["candidate_sources"] = []
    state["collected_notes"] = []
    state["evidence_cards"] = []
    state["run_log"] = []
    return ProgressReporter().report(state, "planning", "Initializing research run.")

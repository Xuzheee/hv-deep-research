from collections.abc import Callable

from app.agent.state import ReportAgentState

ProgressCallback = Callable[[str, str, str], None]


class ProgressReporter:
    def __init__(self, callback: ProgressCallback | None = None) -> None:
        self.callback = callback

    def report(self, state: ReportAgentState, status: str, message: str) -> ReportAgentState:
        state["status"] = status
        state["progress_message"] = message
        if self.callback is not None:
            self.callback(state["report_id"], status, message)
        return state

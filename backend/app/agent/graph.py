from collections.abc import Callable

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    collect_info,
    cross_insights,
    evidence_filter,
    horizontal_analysis,
    initialize_report_run,
    persist_report_artifacts,
    quality_check,
    research_planner,
    synthesis_report_data,
    vertical_analysis,
)
from app.agent.state import ReportAgentState

NODE_SEQUENCE = [
    "initialize_report_run",
    "research_planner",
    "collect_info",
    "evidence_filter",
    "vertical_analysis",
    "horizontal_analysis",
    "cross_insights",
    "synthesis_report_data",
    "quality_check",
    "quality_remediation",
    "persist_report_artifacts",
]

NodeEventCallback = Callable[[str, str, str], None]
NodeFunction = Callable[[ReportAgentState], ReportAgentState]

NODE_STATUS_MESSAGES = {
    "initialize_report_run": "Initializing report run.",
    "research_planner": "Planning source strategy.",
    "collect_info": "Collecting source material.",
    "evidence_filter": "Filtering evidence.",
    "vertical_analysis": "Running vertical analysis.",
    "horizontal_analysis": "Running horizontal analysis.",
    "cross_insights": "Generating cross insights.",
    "synthesis_report_data": "Synthesizing frontend-compatible report data.",
    "quality_check": "Checking report quality.",
    "quality_remediation": "Preparing one quality remediation pass.",
    "persist_report_artifacts": "Saving report artifacts.",
}

def quality_remediation(state: ReportAgentState) -> ReportAgentState:
    state["quality_remediation_attempted"] = True
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "quality_check",
            "message": "Quality remediation triggered; rerunning synthesis once.",
        }
    )
    return {**state, "progress_message": "Prepared one quality remediation pass."}


NODE_FUNCTIONS: dict[str, NodeFunction] = {
    "initialize_report_run": initialize_report_run,
    "research_planner": research_planner,
    "collect_info": collect_info,
    "evidence_filter": evidence_filter,
    "vertical_analysis": vertical_analysis,
    "horizontal_analysis": horizontal_analysis,
    "cross_insights": cross_insights,
    "synthesis_report_data": synthesis_report_data,
    "quality_check": quality_check,
    "quality_remediation": quality_remediation,
    "persist_report_artifacts": persist_report_artifacts,
}


def _route_after_quality_check(state: ReportAgentState) -> str:
    quality_result = state.get("quality_check")
    if quality_result and quality_result.quality_warning and not state.get("quality_remediation_attempted", False):
        return "quality_remediation"
    return "persist_report_artifacts"


def _observe_node(node_name: str, node: NodeFunction, on_node_event: NodeEventCallback | None) -> NodeFunction:
    if on_node_event is None:
        return node

    def observed(state: ReportAgentState) -> ReportAgentState:
        on_node_event(node_name, "running", NODE_STATUS_MESSAGES[node_name])
        try:
            result = node(state)
        except Exception as exc:
            on_node_event(node_name, "failed", str(exc))
            raise
        on_node_event(node_name, "completed", result.get("progress_message", NODE_STATUS_MESSAGES[node_name]))
        return result

    return observed


def build_report_graph(on_node_event: NodeEventCallback | None = None):
    graph = StateGraph(ReportAgentState)
    for node_name in NODE_SEQUENCE:
        graph.add_node(node_name, _observe_node(node_name, NODE_FUNCTIONS[node_name], on_node_event))

    graph.set_entry_point("initialize_report_run")
    graph.add_edge("initialize_report_run", "research_planner")
    graph.add_edge("research_planner", "collect_info")
    graph.add_edge("collect_info", "evidence_filter")
    graph.add_edge("evidence_filter", "vertical_analysis")
    graph.add_edge("vertical_analysis", "horizontal_analysis")
    graph.add_edge("horizontal_analysis", "cross_insights")
    graph.add_edge("cross_insights", "synthesis_report_data")
    graph.add_edge("synthesis_report_data", "quality_check")
    graph.add_conditional_edges(
        "quality_check",
        _route_after_quality_check,
        {
            "quality_remediation": "quality_remediation",
            "persist_report_artifacts": "persist_report_artifacts",
        },
    )
    graph.add_edge("quality_remediation", "synthesis_report_data")
    graph.add_edge("persist_report_artifacts", END)
    return graph.compile()


def run_report_graph(state: ReportAgentState) -> ReportAgentState:
    return build_report_graph().invoke(state)


def run_report_graph_observed(state: ReportAgentState, on_node_event: NodeEventCallback) -> ReportAgentState:
    return build_report_graph(on_node_event).invoke(state)

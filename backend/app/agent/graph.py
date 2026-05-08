from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    collect_info,
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
    "synthesis_report_data",
    "quality_check",
    "persist_report_artifacts",
]


def build_report_graph():
    graph = StateGraph(ReportAgentState)
    graph.add_node("initialize_report_run", initialize_report_run)
    graph.add_node("research_planner", research_planner)
    graph.add_node("collect_info", collect_info)
    graph.add_node("evidence_filter", evidence_filter)
    graph.add_node("vertical_analysis", vertical_analysis)
    graph.add_node("horizontal_analysis", horizontal_analysis)
    graph.add_node("synthesis_report_data", synthesis_report_data)
    graph.add_node("quality_check", quality_check)
    graph.add_node("persist_report_artifacts", persist_report_artifacts)

    graph.set_entry_point("initialize_report_run")
    graph.add_edge("initialize_report_run", "research_planner")
    graph.add_edge("research_planner", "collect_info")
    graph.add_edge("collect_info", "evidence_filter")
    graph.add_edge("evidence_filter", "vertical_analysis")
    graph.add_edge("vertical_analysis", "horizontal_analysis")
    graph.add_edge("horizontal_analysis", "synthesis_report_data")
    graph.add_edge("synthesis_report_data", "quality_check")
    graph.add_edge("quality_check", "persist_report_artifacts")
    graph.add_edge("persist_report_artifacts", END)
    return graph.compile()


def run_report_graph(state: ReportAgentState) -> ReportAgentState:
    return build_report_graph().invoke(state)

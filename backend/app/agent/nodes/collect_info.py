from app.agent.progress_reporter import ProgressReporter
from app.agent.state import ReportAgentState
from app.agent.tools.firecrawl_tool import scrape_firecrawl
from app.agent.tools.tavily_tool import search_tavily

MAX_TOOL_CALLS = 12


def _append_collection_warning(state: ReportAgentState, tool_name: str, exc: Exception) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "collect_info",
            "tool": tool_name,
            "message": f"External collection call failed: {exc.__class__.__name__}",
        }
    )


def collect_info(state: ReportAgentState) -> ReportAgentState:
    tool_calls = 0
    sources = []
    notes = []

    for query in state["research_plan"].initial_queries:
        if tool_calls >= MAX_TOOL_CALLS:
            break
        try:
            query_sources = search_tavily(query, max_results=3)
        except Exception as exc:
            _append_collection_warning(state, "tavily_search", exc)
            tool_calls += 1
            continue
        tool_calls += 1
        for source in query_sources:
            sources.append(source)
            if tool_calls >= MAX_TOOL_CALLS:
                continue
            try:
                notes.append(scrape_firecrawl(source.url, query, source.intended_dimension))
            except Exception as exc:
                source.scrape_failed = True
                _append_collection_warning(state, "firecrawl_scrape", exc)
            tool_calls += 1

    state["candidate_sources"] = sources
    state["collected_notes"] = notes
    state["tool_call_count"] = tool_calls
    return ProgressReporter().report(
        state,
        "filtering",
        f"Collected {len(notes)} notes from {len(sources)} ranked sources.",
    )

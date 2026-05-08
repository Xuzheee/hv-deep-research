from app.agent.progress_reporter import ProgressReporter
from app.agent.state import ReportAgentState
from app.agent.tools.firecrawl_tool import scrape_firecrawl
from app.agent.tools.tavily_tool import search_tavily

MAX_TOOL_CALLS = 12


def collect_info(state: ReportAgentState) -> ReportAgentState:
    tool_calls = 0
    sources = []
    notes = []

    for query in state["research_plan"].initial_queries:
        if tool_calls >= MAX_TOOL_CALLS:
            break
        query_sources = search_tavily(query, max_results=3)
        tool_calls += 1
        for source in query_sources:
            sources.append(source)
            if tool_calls >= MAX_TOOL_CALLS:
                continue
            notes.append(scrape_firecrawl(source.url, query, source.intended_dimension))
            tool_calls += 1

    state["candidate_sources"] = sources
    state["collected_notes"] = notes
    state["tool_call_count"] = tool_calls
    return ProgressReporter().report(
        state,
        "filtering",
        f"Collected {len(notes)} notes from {len(sources)} ranked sources.",
    )

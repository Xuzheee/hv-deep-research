from app.agent.progress_reporter import ProgressReporter
from app.agent.state import ReportAgentState
from app.agent.tools.firecrawl_tool import scrape_firecrawl
from app.agent.tools.tavily_tool import search_tavily

MAX_TOOL_CALLS = 35
MAX_SEARCH_RESULTS_PER_QUERY = 6
MAX_SCRAPES_PER_DOMAIN = 3


def _append_collection_warning(state: ReportAgentState, tool_name: str, exc: Exception) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "collect_info",
            "tool": tool_name,
            "message": f"External collection call failed: {exc.__class__.__name__}",
        }
    )


def _append_coverage_warning(state: ReportAgentState, dimension: str) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "collect_info",
            "message": f"Missing {dimension} collection coverage.",
        }
    )


def collect_info(state: ReportAgentState) -> ReportAgentState:
    tool_calls = 0
    sources = []
    notes = []
    seen_urls = set()
    scrape_counts_by_domain: dict[str, int] = {}

    planned_queries = state["research_plan"].planned_queries or [
        {"query": query, "intended_dimension": "both"} for query in state["research_plan"].initial_queries
    ]

    for planned_query in planned_queries:
        query = planned_query.query if hasattr(planned_query, "query") else planned_query["query"]
        intended_dimension = (
            planned_query.intended_dimension if hasattr(planned_query, "intended_dimension") else planned_query["intended_dimension"]
        )
        if tool_calls >= MAX_TOOL_CALLS:
            break
        try:
            query_sources = search_tavily(query, intended_dimension=intended_dimension, max_results=MAX_SEARCH_RESULTS_PER_QUERY)
        except Exception as exc:
            _append_collection_warning(state, "tavily_search", exc)
            tool_calls += 1
            continue
        tool_calls += 1
        for source in query_sources:
            if source.url in seen_urls:
                continue
            seen_urls.add(source.url)
            sources.append(source)
            if tool_calls >= MAX_TOOL_CALLS:
                continue
            if scrape_counts_by_domain.get(source.source_domain, 0) >= MAX_SCRAPES_PER_DOMAIN:
                continue
            try:
                notes.append(scrape_firecrawl(source.url, query, source.intended_dimension))
                scrape_counts_by_domain[source.source_domain] = scrape_counts_by_domain.get(source.source_domain, 0) + 1
            except Exception as exc:
                source.scrape_failed = True
                _append_collection_warning(state, "firecrawl_scrape", exc)
            tool_calls += 1

    collected_dimensions = {note.intended_dimension for note in notes}
    for dimension in ["vertical", "horizontal"]:
        if dimension not in collected_dimensions:
            _append_coverage_warning(state, dimension)

    state["candidate_sources"] = sources
    state["collected_notes"] = notes
    state["tool_call_count"] = tool_calls
    return ProgressReporter().report(
        state,
        "filtering",
        f"Collected {len(notes)} notes from {len(sources)} ranked sources.",
    )

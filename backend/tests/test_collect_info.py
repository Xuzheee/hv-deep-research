import importlib
from datetime import UTC, datetime

from app.agent.nodes.research_planner import research_planner
from app.agent.schemas.source import CandidateSource, CollectedNote

collect_info_module = importlib.import_module("app.agent.nodes.collect_info")


def test_collect_info_continues_when_one_scrape_times_out(monkeypatch) -> None:
    now = datetime.now(UTC).isoformat()
    state = research_planner(
        {
            "report_id": "rpt_collect_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "candidate_sources": [],
            "collected_notes": [],
            "run_log": [],
        }
    )

    def fake_search(query: str, max_results: int):
        return [
            CandidateSource(
                source_id="src_timeout",
                url="https://example.com/timeout",
                title="Timeout source",
                source_domain="example.com",
                source_type="search_result",
                source_tier="unknown",
                source_score=1.0,
                intended_dimension="both",
                retrieved_at=now,
            ),
            CandidateSource(
                source_id="src_ok",
                url="https://example.com/ok",
                title="Working source",
                source_domain="example.com",
                source_type="search_result",
                source_tier="unknown",
                source_score=1.0,
                intended_dimension="both",
                retrieved_at=now,
            ),
        ]

    def fake_scrape(url: str, query: str, intended_dimension: str):
        if url.endswith("/timeout"):
            raise TimeoutError("network timed out")
        return CollectedNote(
            note_id="note_ok",
            query=query,
            tool_name="firecrawl_scrape",
            title="Working source",
            url=url,
            source_domain="example.com",
            raw_markdown_excerpt="Evidence body",
            intended_dimension="both",
            retrieved_at=now,
        )

    monkeypatch.setattr(collect_info_module, "search_tavily", fake_search)
    monkeypatch.setattr(collect_info_module, "scrape_firecrawl", fake_scrape)

    result = collect_info_module.collect_info(state)

    assert result["status"] == "filtering"
    assert len(result["candidate_sources"]) > len(result["collected_notes"])
    assert result["collected_notes"]
    assert any(log["node"] == "collect_info" for log in result["run_log"])

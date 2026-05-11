import importlib
from datetime import UTC, datetime

from app.agent.nodes.research_planner import research_planner
from app.agent.nodes.collect_info import MAX_SCRAPES_PER_DOMAIN
from app.agent.schemas.source import CandidateSource, CollectedNote

collect_info_module = importlib.import_module("app.agent.nodes.collect_info")
firecrawl_tool_module = importlib.import_module("app.agent.tools.firecrawl_tool")


def test_clean_markdown_excerpt_removes_webpage_boilerplate() -> None:
    markdown = """
# Cursor AI raises new funding

Home
Pricing
Login
Sign up
Just a moment...
Checking your browser before accessing the site.
Cloudflare Ray ID: abc123
Share this article
Cookie preferences
Subscribe to our newsletter
Cursor AI is an AI coding editor used by engineering teams to accelerate software development.
- The company introduced enterprise controls for larger teams.
"""

    cleaned = firecrawl_tool_module._clean_markdown_excerpt(markdown)

    assert "Cursor AI raises new funding" in cleaned
    assert "AI coding editor" in cleaned
    assert "enterprise controls" in cleaned
    assert "Cloudflare" not in cleaned
    assert "Checking your browser" not in cleaned
    assert "Share this article" not in cleaned
    assert "Cookie preferences" not in cleaned
    assert "Subscribe" not in cleaned
    assert "\nHome\n" not in f"\n{cleaned}\n"
    assert "\nLogin\n" not in f"\n{cleaned}\n"



def test_clean_markdown_excerpt_caps_output_length() -> None:
    cleaned = firecrawl_tool_module._clean_markdown_excerpt("A" * 5000, max_chars=4000)

    assert len(cleaned) == 4000



def test_research_planner_creates_commercial_depth_queries() -> None:
    state = research_planner(
        {
            "report_id": "rpt_plan_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "run_log": [],
        }
    )

    queries = state["research_plan"].initial_queries
    query_text = " ".join(queries).lower()

    assert len(queries) >= 6
    assert "official" in query_text
    assert "competitors" in query_text
    assert "limitations" in query_text
    assert "adoption" in query_text or "market" in query_text



def test_research_planner_uses_mixed_chinese_and_english_language() -> None:
    state = research_planner(
        {
            "report_id": "rpt_plan_mix_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "run_log": [],
        }
    )

    plan = state["research_plan"]

    assert "横纵分析" in plan.research_motivation
    assert "origin story" in " ".join(plan.vertical_questions)
    assert "launch" in " ".join(plan.vertical_questions).lower()
    assert "direct competitors" in " ".join(plan.horizontal_questions).lower()
    assert "pricing" in " ".join(plan.horizontal_questions).lower()
    assert "customer signals" in " ".join(plan.supplementary_questions).lower()




def test_collect_info_dedupes_urls_and_caps_scrapes_per_domain(monkeypatch) -> None:
    now = datetime.now(UTC).isoformat()
    state = research_planner(
        {
            "report_id": "rpt_collect_dedupe_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "candidate_sources": [],
            "collected_notes": [],
            "run_log": [],
        }
    )
    scraped_urls = []

    def source(url: str, domain: str) -> CandidateSource:
        return CandidateSource(
            source_id=url.rsplit("/", 1)[-1],
            url=url,
            title=url,
            source_domain=domain,
            source_type="search_result",
            source_tier="unknown",
            source_score=1.0,
            intended_dimension="both",
            retrieved_at=now,
        )

    def fake_search(query: str, max_results: int):
        assert max_results == 4
        return [
            source("https://example.com/a", "example.com"),
            source("https://example.com/a", "example.com"),
            source("https://example.com/b", "example.com"),
            source("https://example.com/c", "example.com"),
            source("https://example.com/d", "example.com"),
            source("https://other.com/a", "other.com"),
        ]

    def fake_scrape(url: str, query: str, intended_dimension: str):
        scraped_urls.append(url)
        return CollectedNote(
            note_id=f"note_{len(scraped_urls)}",
            query=query,
            tool_name="firecrawl_scrape",
            title=url,
            url=url,
            source_domain=url.split("/")[2],
            raw_markdown_excerpt="Evidence body",
            intended_dimension="both",
            retrieved_at=now,
        )

    monkeypatch.setattr(collect_info_module, "search_tavily", fake_search)
    monkeypatch.setattr(collect_info_module, "scrape_firecrawl", fake_scrape)

    result = collect_info_module.collect_info(state)

    assert scraped_urls.count("https://example.com/a") == 1
    assert len([url for url in scraped_urls if "example.com" in url]) == MAX_SCRAPES_PER_DOMAIN
    assert "https://other.com/a" in scraped_urls
    assert result["tool_call_count"] <= collect_info_module.MAX_TOOL_CALLS



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

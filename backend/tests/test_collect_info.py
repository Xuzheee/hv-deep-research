import importlib
from datetime import UTC, datetime

from app.agent.nodes.research_planner import research_planner
from app.agent.nodes.collect_info import MAX_SCRAPES_PER_DOMAIN
from app.agent.schemas.research_plan import PlannedQuery, ResearchPlan
from app.agent.schemas.source import CandidateSource, CollectedNote

collect_info_module = importlib.import_module("app.agent.nodes.collect_info")
research_planner_module = importlib.import_module("app.agent.nodes.research_planner")
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



def test_research_planner_adds_queries_for_source_diversity() -> None:
    state = research_planner(
        {
            "report_id": "rpt_plan_diversity_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "run_log": [],
        }
    )

    query_text = " ".join(state["research_plan"].initial_queries).lower()

    assert "release notes" in query_text
    assert "founder interview" in query_text
    assert "reddit" in query_text
    assert "hacker news" in query_text
    assert "security" in query_text
    assert "compliance" in query_text



def test_research_planner_uses_llm_plan_when_configured(monkeypatch) -> None:
    llm_plan = ResearchPlan(
        subject="Cursor AI",
        subject_type="product",
        research_motivation="LLM planned 横纵分析 research.",
        vertical_questions=["Cursor AI origin story and launch milestones"],
        horizontal_questions=["Cursor AI direct competitors and pricing"],
        supplementary_questions=["Cursor AI customer signals"],
        initial_queries=[
            "Cursor AI official product features",
            "Cursor AI launch history",
            "Cursor AI founder interview",
            "Cursor AI competitors",
            "Cursor AI limitations risks",
            "Cursor AI customer signals",
        ],
        planned_queries=[
            PlannedQuery(query="Cursor AI official product features", intended_dimension="both"),
            PlannedQuery(query="Cursor AI launch history", intended_dimension="vertical"),
            PlannedQuery(query="Cursor AI founder interview", intended_dimension="vertical"),
            PlannedQuery(query="Cursor AI competitors", intended_dimension="horizontal"),
            PlannedQuery(query="Cursor AI limitations risks", intended_dimension="horizontal"),
            PlannedQuery(query="Cursor AI customer signals", intended_dimension="supplementary"),
        ],
        expected_competitors=["GitHub Copilot"],
        source_preferences=["official_blog", "credible_media"],
    )

    monkeypatch.setattr(research_planner_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(research_planner_module, "complete_json", lambda prompt, schema, system_prompt=None: llm_plan)

    state = research_planner(
        {
            "report_id": "rpt_plan_llm_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "run_log": [],
        }
    )

    plan = state["research_plan"]

    assert plan.research_motivation == "LLM planned 横纵分析 research."
    assert {query.intended_dimension for query in plan.planned_queries} >= {"vertical", "horizontal"}
    assert plan.expected_competitors == ["GitHub Copilot"]



def test_research_planner_falls_back_when_llm_plan_is_weak(monkeypatch) -> None:
    weak_plan = ResearchPlan(
        subject="Cursor AI",
        subject_type="product",
        research_motivation="Too weak.",
        vertical_questions=[],
        horizontal_questions=[],
        initial_queries=["Cursor AI"],
        planned_queries=[PlannedQuery(query="Cursor AI", intended_dimension="both")],
    )

    monkeypatch.setattr(research_planner_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(research_planner_module, "complete_json", lambda prompt, schema, system_prompt=None: weak_plan)

    state = research_planner(
        {
            "report_id": "rpt_plan_weak_llm_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "run_log": [],
        }
    )

    plan = state["research_plan"]

    assert len(plan.initial_queries) >= 6
    assert {query.intended_dimension for query in plan.planned_queries} >= {"vertical", "horizontal"}
    assert state["run_log"][0]["node"] == "research_planner"
    assert "weak" in state["run_log"][0]["message"].lower()



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




def test_collect_info_collects_vertical_and_horizontal_dimensions(monkeypatch) -> None:
    now = datetime.now(UTC).isoformat()
    state = research_planner(
        {
            "report_id": "rpt_collect_dimensions_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "candidate_sources": [],
            "collected_notes": [],
            "run_log": [],
        }
    )
    searched_dimensions = []
    scraped_dimensions = []

    def fake_search(query: str, intended_dimension: str, max_results: int):
        searched_dimensions.append(intended_dimension)
        if intended_dimension not in {"vertical", "horizontal"}:
            return []
        return [
            CandidateSource(
                source_id=f"src_{intended_dimension}_{len(searched_dimensions)}",
                url=f"https://{intended_dimension}.example.com/{len(searched_dimensions)}",
                title=f"{intended_dimension} source",
                source_domain=f"{intended_dimension}.example.com",
                source_type="search_result",
                source_tier="unknown",
                source_score=1.0,
                intended_dimension=intended_dimension,
                retrieved_at=now,
            )
        ]

    def fake_scrape(url: str, query: str, intended_dimension: str):
        scraped_dimensions.append(intended_dimension)
        return CollectedNote(
            note_id=f"note_{len(scraped_dimensions)}",
            query=query,
            tool_name="firecrawl_scrape",
            title=url,
            url=url,
            source_domain=url.split("/")[2],
            raw_markdown_excerpt="Evidence body",
            intended_dimension=intended_dimension,
            retrieved_at=now,
        )

    monkeypatch.setattr(collect_info_module, "search_tavily", fake_search)
    monkeypatch.setattr(collect_info_module, "scrape_firecrawl", fake_scrape)

    result = collect_info_module.collect_info(state)

    assert "vertical" in searched_dimensions
    assert "horizontal" in searched_dimensions
    assert "vertical" in scraped_dimensions
    assert "horizontal" in scraped_dimensions
    assert {note.intended_dimension for note in result["collected_notes"]} >= {"vertical", "horizontal"}



def test_collect_info_warns_when_dimension_coverage_is_missing(monkeypatch) -> None:
    now = datetime.now(UTC).isoformat()
    state = research_planner(
        {
            "report_id": "rpt_collect_missing_dimension_test",
            "topic": "Cursor AI",
            "subject": "Cursor AI",
            "subject_type": "product",
            "candidate_sources": [],
            "collected_notes": [],
            "run_log": [],
        }
    )

    def fake_search(query: str, intended_dimension: str, max_results: int):
        if intended_dimension != "vertical":
            return []
        return [
            CandidateSource(
                source_id="src_vertical_only",
                url="https://vertical.example.com/only",
                title="Vertical source",
                source_domain="vertical.example.com",
                source_type="search_result",
                source_tier="unknown",
                source_score=1.0,
                intended_dimension="vertical",
                retrieved_at=now,
            )
        ]

    def fake_scrape(url: str, query: str, intended_dimension: str):
        return CollectedNote(
            note_id="note_vertical_only",
            query=query,
            tool_name="firecrawl_scrape",
            title="Vertical source",
            url=url,
            source_domain="vertical.example.com",
            raw_markdown_excerpt="Evidence body",
            intended_dimension=intended_dimension,
            retrieved_at=now,
        )

    monkeypatch.setattr(collect_info_module, "search_tavily", fake_search)
    monkeypatch.setattr(collect_info_module, "scrape_firecrawl", fake_scrape)

    result = collect_info_module.collect_info(state)

    assert {note.intended_dimension for note in result["collected_notes"]} == {"vertical"}
    assert any(
        log["node"] == "collect_info" and "Missing horizontal collection coverage" in log["message"]
        for log in result["run_log"]
    )



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

    def fake_search(query: str, intended_dimension: str, max_results: int):
        assert max_results == 6
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

    def fake_search(query: str, intended_dimension: str, max_results: int):
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

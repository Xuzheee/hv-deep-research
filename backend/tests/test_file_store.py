import shutil
from pathlib import Path

from app.agent.schemas.quality import QualityCheckResult
from app.agent.schemas.source import CandidateSource
from app.agent.tools.file_store import ReportFileStore
from app.agent.tools.firecrawl_tool import scrape_firecrawl
from app.agent.tools.source_ranker import rank_candidate_sources
from app.agent.tools.tavily_tool import search_tavily


def test_file_store_writes_expected_artifacts() -> None:
    temp_dir = Path("backend/.test-output/file-store")
    shutil.rmtree(temp_dir, ignore_errors=True)
    store = ReportFileStore(temp_dir)

    paths = store.write_report_artifacts(
        "rpt_test",
        report_data={"report_id": "rpt_test"},
        evidence_cards=[],
        raw_sources=[],
        run_log=[{"step": "test"}],
        quality_check=QualityCheckResult(
            quality_warning=False,
            quality_score=90,
            source_count=1,
            evidence_count=1,
        ),
    )

    assert set(paths) == {
        "report_data_path",
        "evidence_cards_path",
        "raw_sources_path",
        "run_log_path",
        "quality_check_path",
    }
    assert store.read_json("rpt_test", "report_data.json") == {"report_id": "rpt_test"}
    assert store.read_json("rpt_test", "quality_check.json")["quality_score"] == 90
    shutil.rmtree(temp_dir)


def test_source_ranker_filters_and_sorts_sources() -> None:
    candidates = [
        CandidateSource(
            source_id="bad",
            url="https://spam.example.com/coupon/gpt-4o",
            title="GPT-4o discount code",
            source_domain="spam.example.com",
            source_type="spam",
            source_tier="unknown",
            source_score=0,
            intended_dimension="both",
            retrieved_at="2026-05-08T00:00:00+00:00",
        ),
        CandidateSource(
            source_id="community",
            url="https://news.ycombinator.com/item?id=1",
            title="GPT-4o discussion",
            source_domain="news.ycombinator.com",
            source_type="community_hn",
            source_tier="unknown",
            source_score=0,
            intended_dimension="horizontal",
            retrieved_at="2026-05-08T00:00:00+00:00",
            freshness="recent",
        ),
        CandidateSource(
            source_id="official",
            url="https://openai.com/index/gpt-4o",
            title="GPT-4o official launch",
            source_domain="openai.com",
            source_type="official_blog",
            source_tier="unknown",
            source_score=0,
            intended_dimension="vertical",
            retrieved_at="2026-05-08T00:00:00+00:00",
            freshness="current",
        ),
    ]

    ranked = rank_candidate_sources(candidates)

    assert [source.source_id for source in ranked] == ["official", "community"]
    assert ranked[0].source_tier == "tier_1_primary"
    assert ranked[0].source_score > ranked[1].source_score


def test_tavily_wrapper_returns_ranked_mock_sources_without_key() -> None:
    results = search_tavily("GPT-4o", max_results=2)

    assert len(results) == 2
    assert results[0].source_id == "src_mock_official"
    assert results[0].source_score > 0


def test_firecrawl_wrapper_returns_mock_note_without_key() -> None:
    note = scrape_firecrawl("https://openai.com/index/gpt-4o", "GPT-4o")

    assert note.tool_name == "firecrawl_scrape"
    assert note.source_domain == "openai.com"
    assert "deterministic mock content" in note.raw_markdown_excerpt

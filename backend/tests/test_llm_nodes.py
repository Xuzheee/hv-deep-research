import importlib

from app.agent.nodes.evidence_filter import evidence_filter
from app.agent.nodes.horizontal_analysis import horizontal_analysis
from app.agent.nodes.vertical_analysis import vertical_analysis
from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.report import (
    CapabilityBoundary,
    CompetitorMatrixItem,
    HorizontalTabData,
    Recommendation,
    VerticalStage,
    VerticalTabData,
)
from app.agent.schemas.source import CollectedNote
from app.agent.state import ReportAgentState


evidence_filter_module = importlib.import_module("app.agent.nodes.evidence_filter")
vertical_analysis_module = importlib.import_module("app.agent.nodes.vertical_analysis")
horizontal_analysis_module = importlib.import_module("app.agent.nodes.horizontal_analysis")


def sample_note() -> CollectedNote:
    return CollectedNote(
        note_id="note_001",
        query="GPT-4o market analysis",
        tool_name="firecrawl_scrape",
        title="GPT-4o source",
        url="https://example.com/gpt-4o",
        source_domain="example.com",
        snippet="GPT-4o evidence snippet.",
        raw_markdown_excerpt="GPT-4o markdown evidence.",
        intended_dimension="both",
        source_type_guess="product_page",
        retrieved_at="2026-05-08T00:00:00Z",
    )


def sample_evidence(evidence_id: str = "ev_001") -> EvidenceCard:
    return EvidenceCard(
        evidence_id=evidence_id,
        claim="GPT-4o has cited evidence.",
        evidence="Evidence body.",
        source_title="GPT-4o source",
        url="https://example.com/gpt-4o",
        source_domain="example.com",
        source_type="product_page",
        source_tier="unknown",
        source_score=1.0,
        dimension="both",
        confidence="medium",
        relevance_score=80,
        freshness="current",
        supporting_quote="Evidence body.",
        retrieved_at="2026-05-08T00:00:00Z",
    )


def base_state() -> ReportAgentState:
    return {
        "report_id": "rpt_test",
        "topic": "GPT-4o",
        "subject": "GPT-4o",
        "subject_type": "product",
        "collected_notes": [sample_note()],
        "evidence_cards": [sample_evidence()],
        "run_log": [],
    }


def test_evidence_filter_uses_llm_cards_when_configured(monkeypatch) -> None:
    state = base_state()
    llm_card = sample_evidence("model_generated")

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(
        evidence_filter_module,
        "complete_json",
        lambda prompt, schema, system_prompt=None: schema(cards=[llm_card]),
    )

    result = evidence_filter(state)

    assert result["evidence_cards"][0].evidence_id == "ev_001"
    assert result["evidence_cards"][0].claim == llm_card.claim
    assert result["run_log"] == []


def test_evidence_filter_falls_back_and_logs_warning_on_llm_error(monkeypatch) -> None:
    state = base_state()

    def raise_llm_error(prompt, schema, system_prompt=None):
        raise ValueError("bad json")

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(evidence_filter_module, "complete_json", raise_llm_error)

    result = evidence_filter(state)

    assert result["evidence_cards"][0].claim == "GPT-4o has relevant evidence from example.com."
    assert result["run_log"][0]["node"] == "evidence_filter"
    assert "ValueError" in result["run_log"][0]["message"]


def test_vertical_analysis_uses_llm_and_filters_unknown_evidence_ids(monkeypatch) -> None:
    state = base_state()
    llm_vertical = VerticalTabData(
        full_text="LLM vertical analysis.",
        stages=[
            VerticalStage(
                stage_id="stage_llm",
                stage_number=1,
                title="LLM stage",
                period="Now",
                summary="LLM summary.",
                key_events=[],
                driving_forces=[],
                path_dependencies=[],
                supporting_evidence_ids=["ev_001", "missing_ev"],
            )
        ],
        key_turning_points=["LLM turning point"],
        path_dependency_summary="LLM path dependency.",
    )

    monkeypatch.setattr(vertical_analysis_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(
        vertical_analysis_module,
        "complete_json",
        lambda prompt, schema, system_prompt=None: llm_vertical,
    )

    result = vertical_analysis(state)

    assert result["vertical"].full_text == "LLM vertical analysis."
    assert result["vertical"].stages[0].supporting_evidence_ids == ["ev_001"]


def test_vertical_analysis_falls_back_and_logs_warning_on_llm_error(monkeypatch) -> None:
    state = base_state()

    def raise_llm_error(prompt, schema, system_prompt=None):
        raise RuntimeError("network")

    monkeypatch.setattr(vertical_analysis_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(vertical_analysis_module, "complete_json", raise_llm_error)

    result = vertical_analysis(state)

    assert result["vertical"].stages[0].stage_id == "stage_001"
    assert result["run_log"][0]["node"] == "vertical_analysis"
    assert "RuntimeError" in result["run_log"][0]["message"]


def test_horizontal_analysis_uses_llm_and_filters_unknown_evidence_ids(monkeypatch) -> None:
    state = base_state()
    llm_horizontal = HorizontalTabData(
        full_text="LLM horizontal analysis.",
        competitor_scenario="few_competitors",
        competitor_matrix=[
            CompetitorMatrixItem(
                competitor_id="comp_llm",
                name="LLM competitor",
                role="Competitor",
                strengths=[],
                weaknesses=[],
                best_for="Researchers",
                pricing_or_access=None,
                supporting_evidence_ids=["ev_001", "bad_ev"],
            )
        ],
        capability_boundaries=[
            CapabilityBoundary(
                boundary_id="boundary_llm",
                title="LLM boundary",
                description="Boundary.",
                boundary_type="current_weakness",
                supporting_evidence_ids=["bad_ev", "ev_001"],
            )
        ],
        positioning_summary="LLM positioning.",
        recommendations=[
            Recommendation(
                rec_id="rec_llm",
                title="LLM recommendation",
                content="Recommendation.",
                priority="medium",
                target_audience="Researchers",
                rationale="Rationale.",
                supporting_evidence_ids=["bad_ev", "ev_001"],
            )
        ],
    )

    monkeypatch.setattr(horizontal_analysis_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(
        horizontal_analysis_module,
        "complete_json",
        lambda prompt, schema, system_prompt=None: llm_horizontal,
    )

    result = horizontal_analysis(state)

    assert result["horizontal"].full_text == "LLM horizontal analysis."
    assert result["horizontal"].competitor_matrix[0].supporting_evidence_ids == ["ev_001"]
    assert result["horizontal"].capability_boundaries[0].supporting_evidence_ids == ["ev_001"]
    assert result["horizontal"].recommendations[0].supporting_evidence_ids == ["ev_001"]


def test_horizontal_analysis_falls_back_and_logs_warning_on_llm_error(monkeypatch) -> None:
    state = base_state()

    def raise_llm_error(prompt, schema, system_prompt=None):
        raise RuntimeError("network")

    monkeypatch.setattr(horizontal_analysis_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(horizontal_analysis_module, "complete_json", raise_llm_error)

    result = horizontal_analysis(state)

    assert result["horizontal"].competitor_matrix[0].competitor_id == "comp_001"
    assert result["run_log"][0]["node"] == "horizontal_analysis"
    assert "RuntimeError" in result["run_log"][0]["message"]

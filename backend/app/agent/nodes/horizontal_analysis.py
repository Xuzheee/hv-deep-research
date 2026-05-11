import json

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_horizontal_analysis_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.report import CapabilityBoundary, CompetitorMatrixItem, HorizontalTabData, Recommendation
from app.agent.state import ReportAgentState


def _append_llm_warning(state: ReportAgentState, node: str, exc: Exception) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": node,
            "message": f"LLM analysis failed; used deterministic fallback: {exc.__class__.__name__}",
        }
    )


def _filter_supporting_ids(ids: list[str], valid_ids: set[str]) -> list[str]:
    return [evidence_id for evidence_id in ids if evidence_id in valid_ids]


def _deterministic_horizontal(state: ReportAgentState) -> HorizontalTabData:
    evidence_ids = [card.evidence_id for card in state["evidence_cards"][:3]]
    subject = state["subject"]
    return HorizontalTabData(
        full_text=f"{subject} is positioned against adjacent products and developer ecosystem signals.",
        competitor_scenario="few_competitors",
        competitor_matrix=[
            CompetitorMatrixItem(
                competitor_id="comp_001",
                name="Adjacent AI research tools",
                role="Alternative workflow category",
                strengths=["Comparable research assistance"],
                weaknesses=["Evidence traceability varies by tool"],
                best_for="Teams evaluating research workflows",
                pricing_or_access=None,
                supporting_evidence_ids=evidence_ids,
            )
        ],
        capability_boundaries=[
            CapabilityBoundary(
                boundary_id="boundary_001",
                title="Evidence quality boundary",
                description="The MVP output is bounded by available sources and deterministic mock adapters.",
                boundary_type="current_weakness",
                supporting_evidence_ids=evidence_ids,
            )
        ],
        positioning_summary=f"{subject} is framed through a small evidence-backed MVP comparison.",
        recommendations=[
            Recommendation(
                rec_id="rec_001",
                title="Validate with live source adapters",
                content="Replace mock tool outputs with real Tavily and Firecrawl calls before using the report for decisions.",
                priority="medium",
                target_audience="product researchers",
                rationale="The MVP proves the workflow shape but not live-source coverage.",
                supporting_evidence_ids=evidence_ids,
            )
        ],
    )


def _llm_horizontal(state: ReportAgentState) -> HorizontalTabData:
    evidence_cards_json = json.dumps(
        [card.model_dump(mode="json") for card in state["evidence_cards"]], ensure_ascii=False
    )
    prompt = build_horizontal_analysis_prompt(state["subject"], evidence_cards_json)
    horizontal = complete_json(prompt, HorizontalTabData, system_prompt=SYSTEM_PROMPT)
    valid_ids = {card.evidence_id for card in state["evidence_cards"]}
    filtered = horizontal.model_copy(
        update={
            "competitor_matrix": [
                item.model_copy(
                    update={"supporting_evidence_ids": _filter_supporting_ids(item.supporting_evidence_ids, valid_ids)}
                )
                for item in horizontal.competitor_matrix
            ],
            "capability_boundaries": [
                boundary.model_copy(
                    update={
                        "supporting_evidence_ids": _filter_supporting_ids(boundary.supporting_evidence_ids, valid_ids)
                    }
                )
                for boundary in horizontal.capability_boundaries
            ],
            "recommendations": [
                recommendation.model_copy(
                    update={
                        "supporting_evidence_ids": _filter_supporting_ids(
                            recommendation.supporting_evidence_ids, valid_ids
                        )
                    }
                )
                for recommendation in horizontal.recommendations
            ],
        }
    )
    if filtered.competitor_matrix:
        return filtered
    return _deterministic_horizontal(state).model_copy(
        update={
            "capability_boundaries": filtered.capability_boundaries or _deterministic_horizontal(state).capability_boundaries,
            "recommendations": filtered.recommendations or _deterministic_horizontal(state).recommendations,
            "full_text": filtered.full_text or _deterministic_horizontal(state).full_text,
            "competitor_scenario": filtered.competitor_scenario or _deterministic_horizontal(state).competitor_scenario,
            "positioning_summary": filtered.positioning_summary or _deterministic_horizontal(state).positioning_summary,
        }
    )


def horizontal_analysis(state: ReportAgentState) -> ReportAgentState:
    horizontal = _deterministic_horizontal(state)
    if is_llm_configured():
        try:
            horizontal = _llm_horizontal(state)
        except Exception as exc:
            _append_llm_warning(state, "horizontal_analysis", exc)

    state["horizontal"] = horizontal
    return ProgressReporter().report(state, "synthesizing", "Completed horizontal analysis.")

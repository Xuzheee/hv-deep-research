import json

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_vertical_analysis_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.report import VerticalStage, VerticalTabData
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


def _deterministic_vertical(state: ReportAgentState) -> VerticalTabData:
    evidence_ids = [card.evidence_id for card in state["evidence_cards"][:3]]
    subject = state["subject"]
    return VerticalTabData(
        full_text=f"{subject} is analyzed through the collected evidence cards for this MVP run.",
        stages=[
            VerticalStage(
                stage_id="stage_001",
                stage_number=1,
                title=f"Initial evidence-backed view of {subject}",
                period="MVP baseline",
                summary=f"The current MVP evidence set establishes a baseline narrative for {subject}.",
                key_events=["Initial research workflow completed"],
                driving_forces=["Evidence-driven product research"],
                path_dependencies=["Available ranked sources and scraped notes"],
                supporting_evidence_ids=evidence_ids,
            )
        ],
        key_turning_points=["Evidence collection completed"],
        path_dependency_summary="The MVP narrative depends on ranked sources and deterministic mock adapters when API keys are absent.",
    )


def _llm_vertical(state: ReportAgentState) -> VerticalTabData:
    evidence_cards_json = json.dumps(
        [card.model_dump(mode="json") for card in state["evidence_cards"]], ensure_ascii=False
    )
    prompt = build_vertical_analysis_prompt(state["subject"], evidence_cards_json)
    vertical = complete_json(prompt, VerticalTabData, system_prompt=SYSTEM_PROMPT)
    valid_ids = {card.evidence_id for card in state["evidence_cards"]}
    return vertical.model_copy(
        update={
            "stages": [
                stage.model_copy(
                    update={"supporting_evidence_ids": _filter_supporting_ids(stage.supporting_evidence_ids, valid_ids)}
                )
                for stage in vertical.stages
            ]
        }
    )


def vertical_analysis(state: ReportAgentState) -> ReportAgentState:
    vertical = _deterministic_vertical(state)
    if is_llm_configured():
        try:
            vertical = _llm_vertical(state)
        except Exception as exc:
            _append_llm_warning(state, "vertical_analysis", exc)

    state["vertical"] = vertical
    return ProgressReporter().report(state, "analyzing_horizontal", "Completed vertical analysis.")

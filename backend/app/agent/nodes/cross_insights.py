import json

from pydantic import BaseModel, Field

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_cross_insights_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.report import CrossInsight
from app.agent.state import ReportAgentState


class CrossInsightResult(BaseModel):
    cross_insights: list[CrossInsight] = Field(default_factory=list)


def _append_llm_warning(state: ReportAgentState, exc: Exception) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "cross_insights",
            "message": f"LLM analysis failed; used deterministic fallback: {exc.__class__.__name__}",
        }
    )


def _filter_supporting_ids(ids: list[str], valid_ids: set[str]) -> list[str]:
    return [evidence_id for evidence_id in ids if evidence_id in valid_ids]


def _deterministic_cross_insights(state: ReportAgentState) -> list[CrossInsight]:
    evidence_ids = [card.evidence_id for card in state["evidence_cards"][:2]]
    subject = state["subject"]
    return [
        CrossInsight(
            insight_id="cross_001",
            title="历史路径如何塑造当前位置",
            content=f"{subject} 的纵向演进路径需要和当前竞争位置一起理解：早期选择与现有能力边界共同决定了它今天的生态位。",
            supporting_evidence_ids=evidence_ids,
        )
    ]


def _llm_cross_insights(state: ReportAgentState) -> list[CrossInsight]:
    evidence_cards_json = json.dumps(
        [card.model_dump(mode="json") for card in state["evidence_cards"]], ensure_ascii=False
    )
    prompt = build_cross_insights_prompt(
        subject=state["subject"],
        vertical_json=state["vertical"].model_dump_json(),
        horizontal_json=state["horizontal"].model_dump_json(),
        evidence_cards_json=evidence_cards_json,
    )
    result = complete_json(prompt, CrossInsightResult, system_prompt=SYSTEM_PROMPT)
    valid_ids = {card.evidence_id for card in state["evidence_cards"]}
    return [
        insight.model_copy(
            update={"supporting_evidence_ids": _filter_supporting_ids(insight.supporting_evidence_ids, valid_ids)}
        )
        for insight in result.cross_insights
    ]


def cross_insights(state: ReportAgentState) -> ReportAgentState:
    insights = _deterministic_cross_insights(state)
    if is_llm_configured():
        try:
            llm_insights = _llm_cross_insights(state)
            if llm_insights:
                insights = llm_insights
        except Exception as exc:
            _append_llm_warning(state, exc)

    state["cross_insights"] = insights
    return ProgressReporter().report(state, "synthesizing", "Generated cross insights.")

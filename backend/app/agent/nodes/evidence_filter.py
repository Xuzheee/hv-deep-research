from pydantic import BaseModel

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_evidence_extraction_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.source import CollectedNote
from app.agent.state import ReportAgentState


class EvidenceExtractionResult(BaseModel):
    cards: list[EvidenceCard]


def _deterministic_evidence_card(state: ReportAgentState, note: CollectedNote, index: int) -> EvidenceCard:
    return EvidenceCard(
        evidence_id=f"ev_{index:03d}",
        claim=f"{state['subject']} has relevant evidence from {note.source_domain}.",
        evidence=note.snippet or note.raw_markdown_excerpt or f"Evidence collected from {note.url}.",
        source_title=note.title,
        url=note.url,
        source_domain=note.source_domain,
        source_type=note.source_type_guess or "mock_scrape",
        source_tier="unknown",
        source_score=1.0,
        dimension=note.intended_dimension,
        confidence="medium",
        relevance_score=75,
        freshness="unknown",
        supporting_quote=note.raw_markdown_excerpt,
        retrieved_at=note.retrieved_at,
        notes="Generated deterministically for the MVP workflow.",
    )


def _deterministic_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    return [
        _deterministic_evidence_card(state, note, index)
        for index, note in enumerate(state["collected_notes"], start=1)
    ]


def _llm_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    cards = []
    for note in state["collected_notes"]:
        prompt = build_evidence_extraction_prompt(state["subject"], note)
        result = complete_json(prompt, EvidenceExtractionResult, system_prompt=SYSTEM_PROMPT)
        cards.extend(result.cards)

    return [card.model_copy(update={"evidence_id": f"ev_{index:03d}"}) for index, card in enumerate(cards, start=1)]


def _append_llm_warning(state: ReportAgentState, node: str, exc: Exception) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": node,
            "message": f"LLM analysis failed; used deterministic fallback: {exc.__class__.__name__}",
        }
    )


def evidence_filter(state: ReportAgentState) -> ReportAgentState:
    cards = _deterministic_evidence_cards(state)
    if is_llm_configured():
        try:
            cards = _llm_evidence_cards(state)
        except Exception as exc:
            _append_llm_warning(state, "evidence_filter", exc)

    state["evidence_cards"] = cards
    return ProgressReporter().report(state, "analyzing_vertical", f"Filtered {len(cards)} evidence cards.")

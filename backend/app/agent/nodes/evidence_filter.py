from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_relevance_selection_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.source import CollectedNote, RelevanceSelectionResult, SelectedPassage
from app.agent.state import ReportAgentState


def _note_from_selected_passage(note: CollectedNote, passage: SelectedPassage) -> CollectedNote:
    return note.model_copy(
        update={
            "snippet": passage.why_it_matters,
            "raw_markdown_excerpt": passage.quote,
            "intended_dimension": passage.dimension,
        }
    )


def _source_tier_for_note(state: ReportAgentState, note: CollectedNote) -> str:
    for source in state.get("candidate_sources", []):
        if source.url == note.url:
            return source.source_tier
    return "unknown"


def _source_score_for_note(state: ReportAgentState, note: CollectedNote) -> float:
    for source in state.get("candidate_sources", []):
        if source.url == note.url:
            return source.source_score
    return 1.0


NOISE_PHRASES = (
    "just a moment",
    "checking your browser",
    "cloudflare",
    "enable javascript",
    "share this",
    "cookie",
    "subscribe",
)



def _has_noise(text: str | None) -> bool:
    lowered = (text or "").lower()
    return any(phrase in lowered for phrase in NOISE_PHRASES)



def _has_enough_text(text: str | None, min_length: int = 20) -> bool:
    return len((text or "").strip()) >= min_length



def _is_usable_evidence_card(card: EvidenceCard, note: CollectedNote) -> bool:
    if card.url != note.url:
        return False
    if card.relevance_score < 50:
        return False
    if not all(
        [
            _has_enough_text(card.claim),
            _has_enough_text(card.evidence),
            _has_enough_text(card.supporting_quote),
        ]
    ):
        return False
    return not any(_has_noise(text) for text in [card.claim, card.evidence, card.supporting_quote])


def _deterministic_evidence_card(state: ReportAgentState, note: CollectedNote, index: int) -> EvidenceCard:
    return EvidenceCard(
        evidence_id=f"ev_{index:03d}",
        claim=f"{state['subject']} has relevant evidence from {note.source_domain}.",
        evidence=note.snippet or note.raw_markdown_excerpt or f"Evidence collected from {note.url}.",
        source_title=note.title,
        url=note.url,
        source_domain=note.source_domain,
        source_type=note.source_type_guess or "mock_scrape",
        source_tier=_source_tier_for_note(state, note),
        source_score=_source_score_for_note(state, note),
        dimension=note.intended_dimension,
        confidence="medium",
        relevance_score=75,
        freshness="unknown",
        supporting_quote=note.raw_markdown_excerpt,
        retrieved_at=note.retrieved_at,
        notes="Generated deterministically for the MVP workflow.",
    )


def _evidence_card_from_selected_passage(
    state: ReportAgentState,
    note: CollectedNote,
    passage: SelectedPassage,
    index: int,
) -> EvidenceCard:
    return EvidenceCard(
        evidence_id=f"ev_{index:03d}",
        claim=passage.why_it_matters,
        evidence=passage.quote,
        source_title=note.title,
        url=note.url,
        source_domain=note.source_domain,
        source_type=note.source_type_guess or "web_source",
        source_tier=_source_tier_for_note(state, note),
        source_score=_source_score_for_note(state, note),
        dimension=passage.dimension,
        confidence="medium",
        relevance_score=passage.relevance_score,
        freshness="unknown",
        supporting_quote=passage.quote,
        retrieved_at=note.retrieved_at,
    )


def _deterministic_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    return [
        _deterministic_evidence_card(state, note, index)
        for index, note in enumerate(state["collected_notes"], start=1)
    ]


def _llm_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    cards = []
    for note in state["collected_notes"]:
        selection_prompt = build_relevance_selection_prompt(state["subject"], note)
        selection = complete_json(selection_prompt, RelevanceSelectionResult, system_prompt=SYSTEM_PROMPT)
        if not selection.is_relevant or not selection.selected_passages:
            continue

        for passage in selection.selected_passages:
            if passage.relevance_score < 50 or _has_noise(passage.quote) or not _has_enough_text(passage.quote):
                continue
            card = _evidence_card_from_selected_passage(state, note, passage, len(cards) + 1)
            if _is_usable_evidence_card(card, _note_from_selected_passage(note, passage)):
                cards.append(card)

    if not cards:
        return _deterministic_evidence_cards(state)
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

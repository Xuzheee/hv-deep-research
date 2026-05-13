import re
from collections import Counter, defaultdict

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_relevance_selection_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceCard, EvidenceGroup
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


MIN_CARD_RELEVANCE_SCORE = 40
MIN_PASSAGE_RELEVANCE_SCORE = 50
MAX_FALLBACK_QUOTE_CHARS = 600
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]*\)")

NOISE_PHRASES = (
    "just a moment",
    "checking your browser",
    "cloudflare",
    "enable javascript",
    "share this",
    "cookie",
    "subscribe",
)

FALLBACK_NAVIGATION_PREFIXES = (
    "Hacker News new past comments ask show",
)



def _has_noise(text: str | None) -> bool:
    lowered = (text or "").lower()
    return any(phrase in lowered for phrase in NOISE_PHRASES)



def _has_enough_text(text: str | None, min_length: int = 20) -> bool:
    return len((text or "").strip()) >= min_length


def _is_usable_note(note: CollectedNote) -> bool:
    content = " ".join(part for part in [note.title, note.snippet, note.raw_markdown_excerpt] if part)
    return _has_enough_text(content) and not _has_noise(content)


def _clean_fallback_quote(text: str | None) -> str:
    cleaned = MARKDOWN_LINK_PATTERN.sub(r"\1", text or "")
    cleaned = cleaned.replace("|", " ")
    cleaned = " ".join(cleaned.split())
    for prefix in FALLBACK_NAVIGATION_PREFIXES:
        cleaned = cleaned.removeprefix(prefix).strip()
    return cleaned[-MAX_FALLBACK_QUOTE_CHARS:]


def _fallback_claim_for_note(state: ReportAgentState, note: CollectedNote) -> str:
    return f"{state['subject']} has source material from {note.source_domain}."



def _is_usable_evidence_card(card: EvidenceCard, note: CollectedNote) -> bool:
    if card.url != note.url:
        return False
    if card.relevance_score < MIN_CARD_RELEVANCE_SCORE:
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
    fallback_quote = _clean_fallback_quote(note.raw_markdown_excerpt or note.snippet or f"Evidence collected from {note.url}.")
    return EvidenceCard(
        evidence_id=f"ev_{index:03d}",
        claim=_fallback_claim_for_note(state, note),
        evidence=note.snippet or fallback_quote,
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
        supporting_quote=fallback_quote,
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


def _dedupe_evidence_cards(cards: list[EvidenceCard]) -> list[EvidenceCard]:
    deduped = []
    seen_keys = set()
    for card in cards:
        quote = " ".join((card.supporting_quote or card.evidence or "").lower().split())
        key = (card.url, quote or card.claim.lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(card)
    return [card.model_copy(update={"evidence_id": f"ev_{index:03d}"}) for index, card in enumerate(deduped, start=1)]


def _deterministic_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    cards = [
        _deterministic_evidence_card(state, note, index)
        for index, note in enumerate([note for note in state["collected_notes"] if _is_usable_note(note)], start=1)
    ]
    return _dedupe_evidence_cards(cards)


def _llm_evidence_cards(state: ReportAgentState) -> list[EvidenceCard]:
    cards = []
    for note in state["collected_notes"]:
        selection_prompt = build_relevance_selection_prompt(state["subject"], note)
        selection = complete_json(selection_prompt, RelevanceSelectionResult, system_prompt=SYSTEM_PROMPT)
        if not selection.is_relevant or not selection.selected_passages:
            continue

        for passage in selection.selected_passages:
            quote_is_usable = not _has_noise(passage.quote) and _has_enough_text(passage.quote)
            if passage.relevance_score < MIN_PASSAGE_RELEVANCE_SCORE or not quote_is_usable:
                continue
            card = _evidence_card_from_selected_passage(state, note, passage, len(cards) + 1)
            if _is_usable_evidence_card(card, _note_from_selected_passage(note, passage)):
                cards.append(card)

    if not cards:
        return _deterministic_evidence_cards(state)
    return _dedupe_evidence_cards(cards)


def _evidence_dimension_label(dimension: str) -> str:
    return {
        "vertical": "纵向证据",
        "horizontal": "横向证据",
        "both": "综合证据",
        "supplementary": "补充证据",
    }.get(dimension, f"{dimension} 证据")


def _build_evidence_groups(cards: list[EvidenceCard]) -> list[EvidenceGroup]:
    grouped_ids: dict[str, list[str]] = defaultdict(list)
    tiers_by_group: dict[str, list[str]] = defaultdict(list)
    domains_by_group: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        grouped_ids[card.dimension].append(card.evidence_id)
        tiers_by_group[card.dimension].append(card.source_tier)
        domains_by_group[card.dimension].add(card.source_domain)

    groups = []
    for index, (dimension, evidence_ids) in enumerate(grouped_ids.items(), start=1):
        tier_counts = Counter(tiers_by_group[dimension])
        groups.append(
            EvidenceGroup(
                group_id=f"group_{index:03d}",
                label=_evidence_dimension_label(dimension),
                description=f"用于{_evidence_dimension_label(dimension).removesuffix('证据')}分析的证据，覆盖 {len(domains_by_group[dimension])} 个来源域名。",
                source_count=len(domains_by_group[dimension]),
                evidence_count=len(evidence_ids),
                dominant_tier=tier_counts.most_common(1)[0][0] if tier_counts else "unknown",
                confidence="medium",
                evidence_ids=evidence_ids,
            )
        )
    return groups


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
    state["evidence_groups"] = _build_evidence_groups(cards)
    return ProgressReporter().report(state, "analyzing_vertical", f"Filtered {len(cards)} evidence cards.")

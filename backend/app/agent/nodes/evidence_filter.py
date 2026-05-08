from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceCard
from app.agent.state import ReportAgentState


def evidence_filter(state: ReportAgentState) -> ReportAgentState:
    cards = []
    for index, note in enumerate(state["collected_notes"], start=1):
        cards.append(
            EvidenceCard(
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
        )

    state["evidence_cards"] = cards
    return ProgressReporter().report(state, "analyzing_vertical", f"Filtered {len(cards)} evidence cards.")

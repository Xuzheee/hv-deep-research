from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.quality import QualityCheckResult
from app.agent.state import ReportAgentState


NOISE_PHRASES = (
    "just a moment",
    "checking your browser",
    "cloudflare",
    "enable javascript",
    "share this",
    "cookie",
    "subscribe",
)


def _known_supporting_ids(state: ReportAgentState) -> set[str]:
    return {card.evidence_id for card in state.get("evidence_cards", [])}


def _has_unknown_ids(ids: list[str], known_ids: set[str]) -> bool:
    return any(evidence_id not in known_ids for evidence_id in ids)


def _has_noisy_quote(state: ReportAgentState) -> bool:
    for card in state.get("evidence_cards", []):
        quote = (card.supporting_quote or "").lower()
        if any(phrase in quote for phrase in NOISE_PHRASES):
            return True
    return False


def quality_check(state: ReportAgentState) -> ReportAgentState:
    report_data = state["report_data"]
    known_ids = _known_supporting_ids(state)
    issues = []
    if report_data.evidence_count == 0:
        issues.append("No evidence cards were generated.")
    if report_data.source_count == 0:
        issues.append("No sources were collected.")
    if report_data.source_count < 8:
        issues.append("Commercial quality target requires at least 8 candidate sources.")
    if report_data.evidence_count < 12:
        issues.append("Commercial quality target requires at least 12 evidence cards.")

    distinct_domains = {card.source_domain for card in state.get("evidence_cards", [])}
    if len(distinct_domains) < 3:
        issues.append("Commercial quality target requires evidence from at least 3 distinct domains.")

    evidence_cards = state.get("evidence_cards", [])
    if evidence_cards:
        high_tier_count = sum(
            1 for card in evidence_cards if card.source_tier in {"tier_1_primary", "tier_2_authoritative_secondary"}
        )
        if high_tier_count / len(evidence_cards) < 0.6:
            issues.append("Tier 1 and Tier 2 evidence should make up at least 60% of evidence cards.")

    if not report_data.overview.key_findings:
        issues.append("Key findings are missing.")
    for finding in report_data.overview.key_findings:
        if not finding.supporting_evidence_ids or _has_unknown_ids(finding.supporting_evidence_ids, known_ids):
            issues.append("Key findings must cite known evidence IDs.")
            break

    for stage in report_data.vertical.stages:
        if _has_unknown_ids(stage.supporting_evidence_ids, known_ids):
            issues.append("Vertical analysis cites unknown evidence IDs.")
            break
    for recommendation in report_data.horizontal.recommendations:
        if _has_unknown_ids(recommendation.supporting_evidence_ids, known_ids):
            issues.append("Horizontal analysis cites unknown evidence IDs.")
            break

    if any("LLM analysis failed" in log.get("message", "") for log in state.get("run_log", [])):
        issues.append("LLM fallback warnings are present in the run log.")
    if _has_noisy_quote(state):
        issues.append("Evidence contains noisy browser, cookie, subscription, or page chrome text.")

    state["quality_check"] = QualityCheckResult(
        quality_warning=bool(issues),
        quality_issues=issues,
        quality_score=max(0, report_data.quality_score - (8 * len(issues))),
        source_count=report_data.source_count,
        evidence_count=report_data.evidence_count,
    )
    report_data.quality_warning = state["quality_check"].quality_warning
    report_data.quality_issues = state["quality_check"].quality_issues
    report_data.quality_score = state["quality_check"].quality_score
    return ProgressReporter().report(state, "persisting", "Completed report quality check.")

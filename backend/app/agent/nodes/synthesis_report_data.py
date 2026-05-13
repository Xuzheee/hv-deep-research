import json
from collections import Counter, defaultdict

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_narrative_report_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.evidence import EvidenceCard, EvidenceGroup, KeyFinding, RiskNote
from app.agent.schemas.report import FutureScenarios, NarrativeReportData, NarrativeSection, OverviewTabData, ReleaseUpdate, ReportData
from app.agent.schemas.source import CandidateSource, SourceItem
from app.agent.state import ReportAgentState


def _top_evidence_cards(evidence_cards: list[EvidenceCard], limit: int = 5) -> list[EvidenceCard]:
    return sorted(evidence_cards, key=lambda card: card.relevance_score, reverse=True)[:limit]


def _build_product_overview(subject: str, evidence_cards: list[EvidenceCard], vertical_text: str, horizontal_text: str) -> str:
    top_claims = "；".join(card.claim for card in _top_evidence_cards(evidence_cards, 3))
    analysis_context = " ".join(part for part in [vertical_text[:300], horizontal_text[:300]] if part)
    if top_claims:
        return f"{subject} 的商业证据显示：{top_claims}。{analysis_context}".strip()
    return f"{subject} 当前缺少足够的商业证据，无法形成可靠的研究摘要。"


def _build_key_findings(evidence_cards: list[EvidenceCard]) -> list[KeyFinding]:
    return [
        KeyFinding(
            finding_id=f"finding_{index:03d}",
            title=f"关键发现 {index}：{card.claim[:70]}",
            content=f"证据显示：{card.evidence}",
            confidence=card.confidence,
            supporting_evidence_ids=[card.evidence_id],
        )
        for index, card in enumerate(_top_evidence_cards(evidence_cards, 5), start=1)
    ]


def _evidence_dimension_label(dimension: str) -> str:
    return {
        "vertical": "纵向证据",
        "horizontal": "横向证据",
        "both": "综合证据",
    }.get(dimension, f"{dimension} 证据")


def _build_evidence_groups(evidence_cards: list[EvidenceCard]) -> list[EvidenceGroup]:
    grouped_ids: dict[str, list[str]] = defaultdict(list)
    tiers_by_group: dict[str, list[str]] = defaultdict(list)
    domains_by_group: dict[str, set[str]] = defaultdict(set)
    for card in evidence_cards:
        grouped_ids[card.dimension].append(card.evidence_id)
        tiers_by_group[card.dimension].append(card.source_tier)
        domains_by_group[card.dimension].add(card.source_domain)

    groups = []
    for index, (dimension, evidence_ids) in enumerate(grouped_ids.items(), start=1):
        tier_counts = Counter(tiers_by_group[dimension])
        dominant_tier = tier_counts.most_common(1)[0][0] if tier_counts else "unknown"
        label = _evidence_dimension_label(dimension)
        groups.append(
            EvidenceGroup(
                group_id=f"group_{index:03d}",
                label=label,
                description=f"用于{label.removesuffix('证据')}分析的证据，覆盖 {len(domains_by_group[dimension])} 个来源域名。",
                source_count=len(domains_by_group[dimension]),
                evidence_count=len(evidence_ids),
                dominant_tier=dominant_tier,
                confidence="medium",
                evidence_ids=evidence_ids,
            )
        )
    return groups


def _build_risk_notes(state: ReportAgentState, evidence_cards: list[EvidenceCard]) -> list[RiskNote]:
    risk_cards = [
        card
        for card in evidence_cards
        if any(keyword in f"{card.claim} {card.evidence}".lower() for keyword in ["risk", "limitation", "weakness", "boundary"])
    ]
    risk_notes = [
        RiskNote(
            risk_id=f"risk_{index:03d}",
            title=f"风险提示 {index}：{card.claim[:70]}",
            content=f"证据提示：{card.evidence}",
            severity="medium",
            supporting_evidence_ids=[card.evidence_id],
        )
        for index, card in enumerate(_top_evidence_cards(risk_cards, 3), start=1)
    ]
    if risk_notes:
        return risk_notes

    boundaries = state["horizontal"].capability_boundaries
    return [
        RiskNote(
            risk_id=f"risk_{index:03d}",
            title=f"风险提示 {index}：{boundary.title}",
            content=f"需要关注：{boundary.description}",
            severity="medium",
            supporting_evidence_ids=boundary.supporting_evidence_ids,
        )
        for index, boundary in enumerate(boundaries[:3], start=1)
    ]


def _has_llm_fallback_warning(state: ReportAgentState) -> bool:
    return any("LLM analysis failed" in log.get("message", "") for log in state.get("run_log", []))


def _source_confidence(source: CandidateSource) -> str:
    if source.source_tier == "tier_1_primary":
        return "high"
    if source.source_tier == "unknown":
        return "low"
    return "medium"


def _build_sources(candidate_sources: list[CandidateSource]) -> list[SourceItem]:
    return [
        SourceItem(
            source_id=source.source_id,
            title=source.title,
            url=source.url,
            source_domain=source.source_domain,
            source_type=source.source_type,
            source_tier=source.source_tier,
            confidence=_source_confidence(source),
            freshness=source.freshness,
            was_scraped=source.was_scraped,
            retrieved_at=source.retrieved_at,
        )
        for source in candidate_sources
    ]


def _build_narrative_report_fallback(
    state: ReportAgentState,
    overview: OverviewTabData,
    evidence_cards: list[EvidenceCard],
) -> NarrativeReportData:
    subject = state["subject"]
    top_evidence = _top_evidence_cards(evidence_cards, 3)
    vertical_sections = [
        NarrativeSection(
            section_id=f"vertical_{index:03d}",
            title=f"纵向演进：{stage.title}",
            content=f"这一阶段的核心变化是：{stage.summary}",
            supporting_evidence_ids=stage.supporting_evidence_ids,
        )
        for index, stage in enumerate(state["vertical"].stages[:3], start=1)
    ]
    if not vertical_sections and top_evidence:
        vertical_sections = [
            NarrativeSection(
                section_id="vertical_001",
                title="纵向演进：证据驱动的产品变化",
                content="现有证据显示，该对象在当前研究窗口内形成了可追踪的演进路径。",
                supporting_evidence_ids=[card.evidence_id for card in top_evidence],
            )
        ]

    horizontal_sections = [
        NarrativeSection(
            section_id=f"horizontal_{index:03d}",
            title=f"横向对比：{item.name}",
            content=f"{item.name} 被定位为 {item.role}，更适合 {item.best_for}。",
            supporting_evidence_ids=item.supporting_evidence_ids,
        )
        for index, item in enumerate(state["horizontal"].competitor_matrix[:3], start=1)
    ]
    if not horizontal_sections and top_evidence:
        horizontal_sections = [
            NarrativeSection(
                section_id="horizontal_001",
                title="横向对比：竞争格局",
                content="当前竞争格局主要由最强证据和相邻替代方案推导得出。",
                supporting_evidence_ids=[card.evidence_id for card in top_evidence],
            )
        ]

    intersection_insights = [
        NarrativeSection(
            section_id="insight_001",
            title="历史路径如何塑造当前位置",
            content=f"{subject} 的早期选择正在影响它今天的竞争位置。",
            supporting_evidence_ids=[card.evidence_id for card in top_evidence[:1]],
        ),
        NarrativeSection(
            section_id="insight_002",
            title="当前市场框架如何放大优势与短板",
            content=f"当前市场框架解释了 {subject} 为什么以现在的方式参与竞争。",
            supporting_evidence_ids=[card.evidence_id for card in top_evidence[:2]],
        ),
    ]

    return NarrativeReportData(
        title=f"{subject} 横纵深度研究报告",
        one_sentence_definition=overview.product_overview[:220],
        opening_judgment=f"综合横向对比与纵向路径，{state['horizontal'].positioning_summary}",
        vertical_story=vertical_sections,
        horizontal_comparison=horizontal_sections,
        intersection_insights=intersection_insights,
        future_scenarios=FutureScenarios(
            most_likely=(
                f"最可能情景：{state['horizontal'].recommendations[0].content}"
                if state["horizontal"].recommendations
                else f"最可能情景：{subject} 沿当前路径继续发展。"
            ),
            most_dangerous=(
                f"最危险情景：{state['horizontal'].capability_boundaries[0].description}"
                if state["horizontal"].capability_boundaries
                else f"最危险情景：{subject} 的差异化窗口继续收窄。"
            ),
            most_optimistic=f"最乐观情景：{subject} 从单点能力扩展为默认工作流入口。",
            supporting_evidence_ids=[card.evidence_id for card in top_evidence],
        ),
        source_notes=[f"证据 {card.evidence_id}：{card.source_title} — {card.url}" for card in top_evidence],
    )


def _filter_narrative_report(report: NarrativeReportData, valid_ids: set[str]) -> NarrativeReportData:
    return report.model_copy(
        update={
            "vertical_story": [
                section.model_copy(update={"supporting_evidence_ids": [evidence_id for evidence_id in section.supporting_evidence_ids if evidence_id in valid_ids]})
                for section in report.vertical_story
            ],
            "horizontal_comparison": [
                section.model_copy(update={"supporting_evidence_ids": [evidence_id for evidence_id in section.supporting_evidence_ids if evidence_id in valid_ids]})
                for section in report.horizontal_comparison
            ],
            "intersection_insights": [
                section.model_copy(update={"supporting_evidence_ids": [evidence_id for evidence_id in section.supporting_evidence_ids if evidence_id in valid_ids]})
                for section in report.intersection_insights
            ],
            "future_scenarios": report.future_scenarios.model_copy(
                update={
                    "supporting_evidence_ids": [
                        evidence_id for evidence_id in report.future_scenarios.supporting_evidence_ids if evidence_id in valid_ids
                    ]
                }
            ),
        }
    )


def _llm_narrative_report(
    state: ReportAgentState,
    overview: OverviewTabData,
    evidence_cards: list[EvidenceCard],
) -> NarrativeReportData:
    evidence_cards_json = json.dumps([card.model_dump(mode="json") for card in evidence_cards], ensure_ascii=False)
    prompt = build_narrative_report_prompt(
        subject=state["subject"],
        overview_json=overview.model_dump_json(),
        vertical_json=state["vertical"].model_dump_json(),
        horizontal_json=state["horizontal"].model_dump_json(),
        evidence_cards_json=evidence_cards_json,
    )
    narrative = complete_json(prompt, NarrativeReportData, system_prompt=SYSTEM_PROMPT)
    valid_ids = {card.evidence_id for card in evidence_cards}
    return _filter_narrative_report(narrative, valid_ids)


def synthesis_report_data(state: ReportAgentState) -> ReportAgentState:
    evidence_cards = state["evidence_cards"]
    subject = state["subject"]
    overview = OverviewTabData(
        product_overview=_build_product_overview(
            subject,
            evidence_cards,
            state["vertical"].full_text,
            state["horizontal"].full_text,
        ),
        release_updates=[
            ReleaseUpdate(
                update_id="update_001",
                title="Research evidence refreshed",
                content=f"Collected {len(evidence_cards)} evidence cards from {len(state['candidate_sources'])} candidate sources for commercial analysis.",
                update_type="other",
                source_url=evidence_cards[0].url if evidence_cards else None,
                confidence="medium",
            )
        ],
        key_findings=_build_key_findings(evidence_cards),
        evidence_groups=_build_evidence_groups(evidence_cards),
        risk_notes=_build_risk_notes(state, evidence_cards),
    )
    narrative_report = _build_narrative_report_fallback(state, overview, evidence_cards)
    if is_llm_configured():
        try:
            narrative_report = _llm_narrative_report(state, overview, evidence_cards)
        except Exception as exc:
            state.setdefault("run_log", []).append(
                {
                    "node": "synthesis_report_data",
                    "level": "warning",
                    "message": "LLM narrative synthesis failed; used Chinese fallback narrative.",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            narrative_report = _build_narrative_report_fallback(state, overview, evidence_cards)
    state["report_data"] = ReportData(
        report_id=state["report_id"],
        topic=state["topic"],
        subject=subject,
        subject_type=state["subject_type"],
        title=f"{subject} 深度研究报告",
        subtitle="基于商业证据的横纵分析报告",
        overview=overview,
        vertical=state["vertical"],
        horizontal=state["horizontal"],
        narrative_report=narrative_report,
        cross_insights=state.get("cross_insights", []),
        recommendations=state["horizontal"].recommendations,
        evidence_cards=evidence_cards,
        evidence_groups=state.get("evidence_groups") or overview.evidence_groups,
        sources=_build_sources(state["candidate_sources"]),
        quality_warning=False,
        quality_issues=[],
        quality_score=90,
        source_count=len(state["candidate_sources"]),
        evidence_count=len(evidence_cards),
        generated_at=evidence_cards[0].retrieved_at if evidence_cards else "2026-05-08T00:00:00+00:00",
        limitations=[] if not _has_llm_fallback_warning(state) else ["LLM fallback was used for part of the report."],
    )
    return ProgressReporter().report(state, "quality_checking", "Synthesized frontend-compatible report data.")

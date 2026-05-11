import importlib

from app.agent.llm import prompts as prompts_module
from app.agent.nodes.evidence_filter import evidence_filter
from app.agent.nodes.horizontal_analysis import horizontal_analysis
from app.agent.nodes.synthesis_report_data import synthesis_report_data
from app.agent.nodes.vertical_analysis import vertical_analysis
from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.report import (
    CapabilityBoundary,
    CompetitorMatrixItem,
    FutureScenarios,
    HorizontalTabData,
    NarrativeReportData,
    NarrativeSection,
    OverviewTabData,
    Recommendation,
    ReleaseUpdate,
    RiskNote,
    VerticalStage,
    VerticalTabData,
)
from app.agent.schemas.source import CandidateSource, CollectedNote
from app.agent.state import ReportAgentState


evidence_filter_module = importlib.import_module("app.agent.nodes.evidence_filter")
vertical_analysis_module = importlib.import_module("app.agent.nodes.vertical_analysis")
horizontal_analysis_module = importlib.import_module("app.agent.nodes.horizontal_analysis")
synthesis_report_data_module = importlib.import_module("app.agent.nodes.synthesis_report_data")


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


def sample_source() -> CandidateSource:
    return CandidateSource(
        source_id="src_001",
        url="https://example.com/gpt-4o",
        title="GPT-4o source",
        source_domain="example.com",
        source_type="product_page",
        source_tier="unknown",
        source_score=1.0,
        intended_dimension="both",
        retrieved_at="2026-05-08T00:00:00Z",
    )


def sample_evidence(evidence_id: str = "ev_001") -> EvidenceCard:
    return EvidenceCard(
        evidence_id=evidence_id,
        claim="GPT-4o has cited evidence.",
        evidence="GPT-4o provides cited product evidence for research workflows.",
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
        supporting_quote="GPT-4o provides cited product evidence for research workflows.",
        retrieved_at="2026-05-08T00:00:00Z",
    )


def base_state() -> ReportAgentState:
    return {
        "report_id": "rpt_test",
        "topic": "GPT-4o",
        "subject": "GPT-4o",
        "subject_type": "product",
        "candidate_sources": [sample_source()],
        "collected_notes": [sample_note()],
        "evidence_cards": [sample_evidence()],
        "run_log": [],
    }


def analyzed_state() -> ReportAgentState:
    state = base_state()
    state["vertical"] = VerticalTabData(
        full_text="Vertical analysis context.",
        stages=[
            VerticalStage(
                stage_id="stage_001",
                stage_number=1,
                title="Launch",
                period="2024",
                summary="The launch created the initial product story.",
                key_events=["Launch"],
                driving_forces=["Demand"],
                path_dependencies=["Earlier work"],
                supporting_evidence_ids=["ev_001"],
            )
        ],
        key_turning_points=["Launch"],
        path_dependency_summary="Launch set the path.",
    )
    state["horizontal"] = HorizontalTabData(
        full_text="Horizontal analysis context.",
        competitor_scenario="few_competitors",
        competitor_matrix=[
            CompetitorMatrixItem(
                competitor_id="comp_001",
                name="Claude",
                role="Direct competitor",
                strengths=["Reasoning"],
                weaknesses=["Evidence traceability"],
                best_for="Knowledge work",
                pricing_or_access=None,
                supporting_evidence_ids=["ev_001"],
            )
        ],
        capability_boundaries=[
            CapabilityBoundary(
                boundary_id="boundary_001",
                title="Access boundary",
                description="Current access differs across plans.",
                boundary_type="current_weakness",
                supporting_evidence_ids=["ev_001"],
            )
        ],
        positioning_summary="Current positioning summary.",
        recommendations=[
            Recommendation(
                rec_id="rec_001",
                title="Keep collecting evidence",
                content="Continue validating the competitive frame.",
                priority="medium",
                target_audience="researchers",
                rationale="More evidence will improve the narrative.",
                supporting_evidence_ids=["ev_001"],
            )
        ],
    )
    return state


def test_evidence_filter_uses_llm_cards_when_configured(monkeypatch) -> None:
    state = base_state()
    llm_card = sample_evidence("model_generated")

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    def fake_complete_json(prompt, schema, system_prompt=None):
        if schema.__name__ == "RelevanceSelectionResult":
            return schema(
                is_relevant=True,
                relevance_reason="Useful product evidence.",
                selected_passages=[
                    {
                        "quote": llm_card.supporting_quote,
                        "why_it_matters": "Useful product evidence.",
                        "dimension": "both",
                        "relevance_score": 80,
                    }
                ],
            )
        return schema(cards=[llm_card])

    monkeypatch.setattr(evidence_filter_module, "complete_json", fake_complete_json)

    result = evidence_filter(state)

    assert result["evidence_cards"][0].evidence_id == "ev_001"
    assert result["evidence_cards"][0].claim == "Useful product evidence."
    assert result["run_log"] == []


def test_evidence_filter_discards_noisy_llm_cards_and_uses_note_fallback(monkeypatch) -> None:
    state = base_state()
    noisy_card = sample_evidence("model_generated")
    noisy_card.supporting_quote = "Just a moment Checking your browser Cloudflare"

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    def fake_complete_json(prompt, schema, system_prompt=None):
        if schema.__name__ == "RelevanceSelectionResult":
            return schema(
                is_relevant=True,
                relevance_reason="Useful product evidence.",
                selected_passages=[
                    {
                        "quote": noisy_card.supporting_quote,
                        "why_it_matters": "Useful product evidence.",
                        "dimension": "both",
                        "relevance_score": 80,
                    }
                ],
            )
        return schema(cards=[noisy_card])

    monkeypatch.setattr(evidence_filter_module, "complete_json", fake_complete_json)

    result = evidence_filter(state)

    assert result["evidence_cards"][0].evidence_id == "ev_001"
    assert result["evidence_cards"][0].claim == "GPT-4o has relevant evidence from example.com."
    assert result["run_log"] == []



def test_evidence_filter_uses_selected_passage_dimensions(monkeypatch) -> None:
    state = base_state()

    def fake_complete_json(prompt, schema, system_prompt=None):
        if schema.__name__ == "RelevanceSelectionResult":
            return schema(
                is_relevant=True,
                relevance_reason="Useful differentiated evidence.",
                selected_passages=[
                    {
                        "quote": "GPT-4o launched with adoption milestones and product evolution evidence.",
                        "why_it_matters": "Shows product evolution.",
                        "dimension": "vertical",
                        "relevance_score": 85,
                    },
                    {
                        "quote": "GPT-4o competes on capability boundaries and enterprise access evidence.",
                        "why_it_matters": "Shows competitive positioning.",
                        "dimension": "horizontal",
                        "relevance_score": 90,
                    },
                ],
            )
        raise AssertionError("Evidence filter should not call a second LLM extraction pass")

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(evidence_filter_module, "complete_json", fake_complete_json)

    result = evidence_filter(state)

    assert [card.dimension for card in result["evidence_cards"]] == ["vertical", "horizontal"]
    assert [card.relevance_score for card in result["evidence_cards"]] == [85, 90]


def test_evidence_filter_propagates_source_tier_into_cards(monkeypatch) -> None:
    state = base_state()
    state["candidate_sources"][0].source_tier = "tier_1_primary"

    def fake_complete_json(prompt, schema, system_prompt=None):
        if schema.__name__ == "RelevanceSelectionResult":
            return schema(
                is_relevant=True,
                relevance_reason="Useful product evidence.",
                selected_passages=[
                    {
                        "quote": "GPT-4o provides cited product evidence for research workflows.",
                        "why_it_matters": "Useful product evidence.",
                        "dimension": "both",
                        "relevance_score": 88,
                    }
                ],
            )
        raise AssertionError("Evidence filter should not call a second LLM extraction pass")

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(evidence_filter_module, "complete_json", fake_complete_json)

    result = evidence_filter(state)

    assert result["evidence_cards"][0].source_tier == "tier_1_primary"



def test_evidence_filter_skips_irrelevant_llm_notes_and_uses_fallback_if_empty(monkeypatch) -> None:
    state = base_state()

    monkeypatch.setattr(evidence_filter_module, "is_llm_configured", lambda: True)
    monkeypatch.setattr(
        evidence_filter_module,
        "complete_json",
        lambda prompt, schema, system_prompt=None: schema(
            is_relevant=False,
            relevance_reason="No useful substance.",
            selected_passages=[],
        ),
    )

    result = evidence_filter(state)

    assert result["evidence_cards"][0].claim == "GPT-4o has relevant evidence from example.com."



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


def test_horizontal_analysis_backfills_competitor_matrix_when_llm_omits_it(monkeypatch) -> None:
    state = base_state()
    llm_horizontal = HorizontalTabData(
        full_text="LLM horizontal analysis.",
        competitor_scenario="mature_market",
        competitor_matrix=[],
        capability_boundaries=[
            CapabilityBoundary(
                boundary_id="boundary_llm",
                title="LLM boundary",
                description="Boundary.",
                boundary_type="current_weakness",
                supporting_evidence_ids=["ev_001"],
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
                supporting_evidence_ids=["ev_001"],
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

    assert result["horizontal"].competitor_matrix
    assert result["horizontal"].competitor_matrix[0].supporting_evidence_ids == ["ev_001"]



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


def test_build_narrative_report_prompt_requires_chinese_report_content() -> None:
    overview = OverviewTabData(
        product_overview="A multimodal assistant.",
        release_updates=[
            ReleaseUpdate(
                update_id="upd_1",
                date="2024-05-13",
                title="Launch",
                content="GPT-4o launched.",
                update_type="product_launch",
                source_url="https://example.com/launch",
                confidence="high",
            )
        ],
        key_findings=[],
        evidence_groups=[],
        risk_notes=[
            RiskNote(
                risk_id="risk_1",
                title="Limited evidence",
                content="Use only supplied evidence.",
                severity="low",
                supporting_evidence_ids=["ev_001"],
            )
        ],
    )

    prompt = prompts_module.build_narrative_report_prompt(
        subject="GPT-4o",
        overview_json=overview.model_dump_json(),
        vertical_json='{"full_text":"Vertical context.","stages":[],"key_turning_points":[],"path_dependency_summary":"Path"}',
        horizontal_json='{"full_text":"Horizontal context.","competitor_scenario":"few_competitors","competitor_matrix":[],"capability_boundaries":[],"positioning_summary":"Positioning","recommendations":[]}',
        evidence_cards_json='[{"evidence_id":"ev_001","claim":"Claim","evidence":"Evidence"}]',
    )

    assert "报告内容必须使用中文" in prompt
    assert "英文产品名、公司名、URL、evidence_id 保持原样" in prompt
    assert "不要写咨询式摘要" in prompt
    assert "纵向部分必须读起来像故事" in prompt
    assert "横向部分必须解释每个竞争者是什么样" in prompt
    assert "supporting_evidence_ids" in prompt
    assert "不要编造事实" in prompt
    assert "信息不足时必须明确说明" in prompt


def test_synthesis_report_data_uses_llm_narrative_and_filters_invalid_evidence_ids(monkeypatch) -> None:
    state = analyzed_state()
    llm_narrative = NarrativeReportData(
        title="GPT-4o 深度研究报告",
        one_sentence_definition="GPT-4o 是具备实时交互能力的多模态助手。",
        opening_judgment="LLM 生成的开场判断。",
        vertical_story=[
            NarrativeSection(
                section_id="vertical_001",
                title="从发布到使用模式",
                content="发布改变了产品的使用模式。",
                supporting_evidence_ids=["ev_001", "missing_ev"],
            )
        ],
        horizontal_comparison=[
            NarrativeSection(
                section_id="horizontal_001",
                title="竞争格局",
                content="它在访问方式和工作流适配上与直接替代品并列竞争。",
                supporting_evidence_ids=["ev_001", "missing_ev"],
            )
        ],
        intersection_insights=[
            NarrativeSection(
                section_id="insight_001",
                title="历史选择塑造当前位置",
                content="早期选择解释了当下位置。",
                supporting_evidence_ids=["missing_ev", "ev_001"],
            )
        ],
        future_scenarios=FutureScenarios(
            most_likely="最可能的结果。",
            most_dangerous="最危险的结果。",
            most_optimistic="最乐观的结果。",
            supporting_evidence_ids=["missing_ev", "ev_001"],
        ),
        source_notes=["来源说明 1", "来源说明 2"],
    )

    prompt_calls: list[str] = []

    monkeypatch.setattr(synthesis_report_data_module, "is_llm_configured", lambda: True, raising=False)

    def fake_complete_json(prompt, schema, system_prompt=None):
        prompt_calls.append(prompt)
        assert schema is NarrativeReportData
        return llm_narrative

    monkeypatch.setattr(synthesis_report_data_module, "complete_json", fake_complete_json, raising=False)

    result = synthesis_report_data(state)

    assert prompt_calls
    assert "报告内容必须使用中文" in prompt_calls[0]
    assert "supporting_evidence_ids" in prompt_calls[0]
    assert result["report_data"].title == "GPT-4o 深度研究报告"
    assert result["report_data"].subtitle == "基于商业证据的横纵分析报告"
    assert result["report_data"].narrative_report is not None
    assert result["report_data"].narrative_report.title == "GPT-4o 深度研究报告"
    assert result["report_data"].narrative_report.opening_judgment == "LLM 生成的开场判断。"
    assert result["report_data"].narrative_report.vertical_story[0].supporting_evidence_ids == ["ev_001"]
    assert result["report_data"].narrative_report.horizontal_comparison[0].supporting_evidence_ids == ["ev_001"]
    assert result["report_data"].narrative_report.intersection_insights[0].supporting_evidence_ids == ["ev_001"]
    assert result["report_data"].narrative_report.future_scenarios.supporting_evidence_ids == ["ev_001"]
    assert result["report_data"].narrative_report.source_notes == ["来源说明 1", "来源说明 2"]
    assert result["report_data"].limitations == []


def test_synthesis_report_data_fallback_outputs_chinese_report_content(monkeypatch) -> None:
    state = analyzed_state()
    monkeypatch.setattr(synthesis_report_data_module, "is_llm_configured", lambda: False, raising=False)

    result = synthesis_report_data(state)
    report_data = result["report_data"]
    narrative = report_data.narrative_report

    assert report_data.title == "GPT-4o 深度研究报告"
    assert report_data.subtitle == "基于商业证据的横纵分析报告"
    assert report_data.overview.product_overview.startswith("GPT-4o 的商业证据显示")
    assert report_data.overview.key_findings[0].title.startswith("关键发现")
    assert report_data.overview.evidence_groups[0].label == "综合证据"
    assert report_data.overview.evidence_groups[0].description.startswith("用于综合分析的证据")
    assert narrative is not None
    assert narrative.title == "GPT-4o 横纵深度研究报告"
    assert narrative.one_sentence_definition.startswith("GPT-4o 的商业证据显示")
    assert narrative.vertical_story[0].title == "纵向演进：Launch"
    assert narrative.horizontal_comparison[0].title == "横向对比：Claude"
    assert narrative.intersection_insights[0].title == "历史路径如何塑造当前位置"
    assert narrative.future_scenarios.most_likely.startswith("最可能情景：")
    assert narrative.future_scenarios.most_dangerous.startswith("最危险情景：")
    assert narrative.future_scenarios.most_optimistic.startswith("最乐观情景：")
    assert narrative.source_notes[0].startswith("证据 ev_001：")


def test_synthesis_report_data_logs_warning_when_llm_narrative_fails(monkeypatch) -> None:
    state = analyzed_state()
    monkeypatch.setattr(synthesis_report_data_module, "is_llm_configured", lambda: True, raising=False)

    def raise_llm_error(prompt, schema, system_prompt=None):
        raise RuntimeError("upstream parse failed")

    monkeypatch.setattr(synthesis_report_data_module, "complete_json", raise_llm_error, raising=False)

    result = synthesis_report_data(state)

    assert result["report_data"].narrative_report.title == "GPT-4o 横纵深度研究报告"
    assert result["run_log"][-1]["node"] == "synthesis_report_data"
    assert result["run_log"][-1]["level"] == "warning"
    assert result["run_log"][-1]["message"] == "LLM narrative synthesis failed; used Chinese fallback narrative."
    assert "RuntimeError" in result["run_log"][-1]["error"]



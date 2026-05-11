from pydantic import ValidationError

from app.agent.schemas.evidence import EvidenceCard
from app.agent.schemas.report import NarrativeReportData, ReportData


def sample_report_data() -> dict:
    return {
        "report_id": "rpt_test",
        "topic": "GPT-4o",
        "subject": "GPT-4o",
        "subject_type": "product",
        "title": "GPT-4o Research Report",
        "subtitle": None,
        "overview": {
            "product_overview": "A multimodal model.",
            "release_updates": [
                {
                    "update_id": "upd_1",
                    "date": "2024-05-13",
                    "title": "Launch",
                    "content": "GPT-4o launched.",
                    "update_type": "product_launch",
                    "source_url": "https://example.com/launch",
                    "confidence": "high",
                }
            ],
            "key_findings": [
                {
                    "finding_id": "kf_1",
                    "title": "Multimodal focus",
                    "content": "The product focuses on multimodal interaction.",
                    "confidence": "high",
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
            "evidence_groups": [
                {
                    "group_id": "grp_1",
                    "label": "Launch evidence",
                    "description": "Primary launch sources.",
                    "source_count": 1,
                    "evidence_count": 1,
                    "dominant_tier": "tier_1_primary",
                    "confidence": "high",
                    "evidence_ids": ["ev_1"],
                }
            ],
            "risk_notes": [
                {
                    "risk_id": "risk_1",
                    "title": "Limited evidence",
                    "content": "MVP report uses limited sources.",
                    "severity": "low",
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
        },
        "vertical": {
            "full_text": "GPT-4o evolved from earlier multimodal work.",
            "stages": [
                {
                    "stage_id": "stage_1",
                    "stage_number": 1,
                    "title": "Launch",
                    "period": "2024",
                    "summary": "Initial public launch.",
                    "key_events": ["Launch"],
                    "driving_forces": ["Multimodal demand"],
                    "path_dependencies": ["Prior model releases"],
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
            "key_turning_points": ["Launch"],
            "path_dependency_summary": "Built on prior model releases.",
        },
        "horizontal": {
            "full_text": "GPT-4o competes with other multimodal assistants.",
            "competitor_scenario": "few_competitors",
            "competitor_matrix": [
                {
                    "competitor_id": "comp_1",
                    "name": "Claude",
                    "role": "AI assistant",
                    "strengths": ["Reasoning"],
                    "weaknesses": ["Limited source evidence in this MVP sample"],
                    "best_for": "Knowledge work",
                    "pricing_or_access": None,
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
            "capability_boundaries": [
                {
                    "boundary_id": "bound_1",
                    "title": "Multimodal capability",
                    "description": "Voice and image interaction boundaries.",
                    "boundary_type": "short_term_feature",
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
            "positioning_summary": "Positioned as a multimodal assistant.",
            "recommendations": [
                {
                    "rec_id": "rec_1",
                    "title": "Compare against direct alternatives",
                    "content": "Use evidence-backed comparison.",
                    "priority": "medium",
                    "target_audience": "product teams",
                    "rationale": "Positioning needs competitor context.",
                    "supporting_evidence_ids": ["ev_1"],
                }
            ],
        },
        "quality_warning": False,
        "quality_issues": [],
        "quality_score": 88,
        "source_count": 1,
        "evidence_count": 1,
        "generated_at": "2026-05-08T00:00:00+00:00",
        "limitations": ["MVP sample data"],
    }


def test_report_data_matches_frontend_shape() -> None:
    report = ReportData.model_validate(sample_report_data())

    dumped = report.model_dump()

    assert dumped["report_id"] == "rpt_test"
    assert dumped["overview"]["key_findings"][0]["supporting_evidence_ids"] == ["ev_1"]
    assert dumped["horizontal"]["recommendations"][0]["priority"] == "medium"
    assert dumped["quality_score"] == 88


def test_report_data_accepts_narrative_report_for_web_output() -> None:
    payload = sample_report_data()
    payload["narrative_report"] = {
        "title": "GPT-4o 横纵分析报告",
        "one_sentence_definition": "GPT-4o is a multimodal assistant positioned around real-time interaction.",
        "opening_judgment": "Its importance comes from shifting the assistant interface toward lower-latency multimodal work.",
        "vertical_story": [
            {
                "section_id": "vertical_1",
                "title": "From model release to interaction layer",
                "content": "GPT-4o's launch connected prior multimodal work to a faster consumer-facing assistant experience.",
                "supporting_evidence_ids": ["ev_1"],
            }
        ],
        "horizontal_comparison": [
            {
                "section_id": "horizontal_1",
                "title": "The competitive frame",
                "content": "GPT-4o competes with other multimodal assistants on latency, access, and workflow fit.",
                "supporting_evidence_ids": ["ev_1"],
            }
        ],
        "intersection_insights": [
            {
                "section_id": "insight_1",
                "title": "Speed became positioning",
                "content": "The historical push toward multimodality shaped its current competitive narrative around interaction speed.",
                "supporting_evidence_ids": ["ev_1"],
            }
        ],
        "future_scenarios": {
            "most_likely": "GPT-4o remains a mainstream multimodal assistant while competitors narrow the feature gap.",
            "most_dangerous": "Competing assistants match the interaction layer while offering stronger enterprise controls.",
            "most_optimistic": "It becomes the default interface for everyday multimodal knowledge work.",
            "supporting_evidence_ids": ["ev_1"],
        },
        "source_notes": ["Launch evidence from example.com."],
    }

    dumped = ReportData.model_validate(payload).model_dump()

    assert dumped["narrative_report"]["vertical_story"][0]["supporting_evidence_ids"] == ["ev_1"]
    assert dumped["narrative_report"]["future_scenarios"]["most_likely"].startswith("GPT-4o")


def test_narrative_report_requires_evidence_backed_sections() -> None:
    payload = {
        "title": "GPT-4o 横纵分析报告",
        "one_sentence_definition": "GPT-4o is a multimodal assistant.",
        "opening_judgment": "Its importance is in the interface shift.",
        "vertical_story": [],
        "horizontal_comparison": [],
        "intersection_insights": [],
        "future_scenarios": {
            "most_likely": "Likely outcome.",
            "most_dangerous": "Dangerous outcome.",
            "most_optimistic": "Optimistic outcome.",
            "supporting_evidence_ids": [],
        },
        "source_notes": [],
    }

    narrative = NarrativeReportData.model_validate(payload)

    assert narrative.title == "GPT-4o 横纵分析报告"
    assert narrative.future_scenarios.most_likely == "Likely outcome."


def test_report_data_rejects_invalid_subject_type() -> None:
    payload = sample_report_data()
    payload["subject_type"] = "invalid"

    try:
        ReportData.model_validate(payload)
    except ValidationError as exc:
        assert "subject_type" in str(exc)
    else:
        raise AssertionError("ReportData accepted an invalid subject_type")


def test_evidence_card_validates_score_bounds() -> None:
    try:
        EvidenceCard.model_validate(
            {
                "evidence_id": "ev_1",
                "claim": "GPT-4o launched in 2024.",
                "evidence": "Launch article excerpt.",
                "source_title": "Launch",
                "url": "https://example.com",
                "source_domain": "example.com",
                "source_type": "official_blog",
                "source_tier": "tier_1_primary",
                "source_score": 1.0,
                "dimension": "both",
                "confidence": "high",
                "relevance_score": 101,
                "freshness": "current",
                "retrieved_at": "2026-05-08T00:00:00+00:00",
            }
        )
    except ValidationError as exc:
        assert "relevance_score" in str(exc)
    else:
        raise AssertionError("EvidenceCard accepted relevance_score above 100")

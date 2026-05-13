import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes_reports import reset_report_runner, set_report_runner
from app.main import app

OUTPUT_DIR = Path("backend/.test-output/api-reports")


def setup_function() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)


def teardown_function() -> None:
    reset_report_runner()
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)


def test_reports_api_creates_completed_report_and_returns_detail() -> None:
    app.dependency_overrides.clear()
    set_report_runner(make_test_runner())
    client = TestClient(app)

    response = client.post("/api/reports", json={"topic": "GPT-4o", "subject_type": "product"})

    assert response.status_code == 200
    created = response.json()["report"]
    assert created["topic"] == "GPT-4o"
    assert created["status"] == "pending"
    assert created["report_data"] is None

    report_id = created["report_id"]
    detail_response = client.get(f"/api/reports/{report_id}")
    detail = detail_response.json()["report"]

    assert detail_response.status_code == 200
    assert detail["status"] == "completed"
    assert detail["quality_score"] == 88
    assert detail["report_data"]["report_id"] == report_id
    assert detail["report_data"]["overview"]["key_findings"]


def test_reports_api_lists_reports_without_detail_payload() -> None:
    app.dependency_overrides.clear()
    set_report_runner(make_test_runner())
    client = TestClient(app)

    client.post("/api/reports", json={"topic": "Claude Code", "subject_type": "product"})

    response = client.get("/api/reports")
    reports = response.json()

    assert response.status_code == 200
    assert len(reports) >= 1
    assert reports[0]["topic"] == "Claude Code"
    assert reports[0]["status"] == "completed"
    assert reports[0]["report_data"] is None


def test_reports_api_returns_status_progress_steps() -> None:
    app.dependency_overrides.clear()
    set_report_runner(make_test_runner())
    client = TestClient(app)

    created = client.post("/api/reports", json={"topic": "Firecrawl", "subject_type": "technology"}).json()["report"]

    response = client.get(f"/api/reports/{created['report_id']}/status")
    status = response.json()

    assert response.status_code == 200
    assert status["status"] == "completed"
    assert status["progress_message"] == "Saved report artifacts."
    assert [step["label"] for step in status["progress_steps"]] == [
        "create_report",
        "initialize_report_run",
        "initialize_report_run",
        "research_planner",
        "research_planner",
        "collect_info",
        "collect_info",
        "evidence_filter",
        "evidence_filter",
        "vertical_analysis",
        "vertical_analysis",
        "horizontal_analysis",
        "horizontal_analysis",
        "cross_insights",
        "cross_insights",
        "synthesis_report_data",
        "synthesis_report_data",
        "quality_check",
        "quality_check",
        "persist_report_artifacts",
        "persist_report_artifacts",
    ]
    assert [step["status"] for step in status["progress_steps"][1:]] == [
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
        "running",
        "completed",
    ]


def test_reports_api_returns_404_for_missing_report() -> None:
    client = TestClient(app)

    detail_response = client.get("/api/reports/missing")
    status_response = client.get("/api/reports/missing/status")

    assert detail_response.status_code == 404
    assert status_response.status_code == 404


def make_test_runner():
    def run(state, on_node_event=None):
        def emit(node_name: str, status: str, message: str) -> None:
            if on_node_event is not None:
                on_node_event(node_name, status, message)

        emit("initialize_report_run", "running", "Initializing report run.")
        emit("initialize_report_run", "completed", "Initialized report run.")
        emit("research_planner", "running", "Planning source strategy.")
        emit("research_planner", "completed", "Planned source strategy.")
        emit("collect_info", "running", "Collecting source material.")
        emit("collect_info", "completed", "Collected source material.")
        emit("evidence_filter", "running", "Filtering evidence.")
        emit("evidence_filter", "completed", "Filtered evidence.")
        emit("vertical_analysis", "running", "Running vertical analysis.")
        emit("vertical_analysis", "completed", "Ran vertical analysis.")
        emit("horizontal_analysis", "running", "Running horizontal analysis.")
        emit("horizontal_analysis", "completed", "Ran horizontal analysis.")
        emit("cross_insights", "running", "Generating cross insights.")
        emit("cross_insights", "completed", "Generated cross insights.")
        emit("synthesis_report_data", "running", "Synthesizing frontend-compatible report data.")
        emit("synthesis_report_data", "completed", "Synthesized frontend-compatible report data.")
        emit("quality_check", "running", "Checking report quality.")
        emit("quality_check", "completed", "Checked report quality.")
        emit("persist_report_artifacts", "running", "Saving report artifacts.")
        from app.agent.schemas.evidence import EvidenceCard
        from app.agent.schemas.quality import QualityCheckResult
        from app.agent.schemas.report import (
            CapabilityBoundary,
            CompetitorMatrixItem,
            HorizontalTabData,
            OverviewTabData,
            Recommendation,
            KeyFinding,
            ReportData,
            VerticalStage,
            VerticalTabData,
        )
        from app.agent.schemas.source import CandidateSource
        from app.agent.tools.file_store import ReportFileStore

        source = CandidateSource(
            source_id="src_001",
            title="Official source",
            url="https://example.com/research",
            snippet="A reliable test source.",
            source_domain="example.com",
            source_type="official",
            intended_dimension="both",
            freshness="current",
            source_tier="tier_1_primary",
            source_score=4.0,
            retrieved_at="2026-05-08T00:00:00+00:00",
        )
        evidence = EvidenceCard(
            evidence_id="ev_001",
            claim="The report was generated.",
            evidence="The API test runner produced deterministic report data.",
            source_title=source.title,
            url=source.url,
            source_domain=source.source_domain,
            source_type="official",
            source_tier=source.source_tier,
            source_score=source.source_score,
            dimension="both",
            confidence="high",
            relevance_score=95,
            freshness="current",
            retrieved_at="2026-05-08T00:00:00+00:00",
        )
        vertical = VerticalTabData(
            full_text="Vertical analysis.",
            stages=[
                VerticalStage(
                    stage_id="stage_001",
                    stage_number=1,
                    title="MVP stage",
                    summary="The MVP report is generated.",
                    supporting_evidence_ids=[evidence.evidence_id],
                )
            ],
            key_turning_points=["MVP workflow completed"],
            path_dependency_summary="The API depends on graph artifacts.",
        )
        horizontal = HorizontalTabData(
            full_text="Horizontal analysis.",
            competitor_scenario="few_competitors",
            competitor_matrix=[
                CompetitorMatrixItem(
                    competitor_id="comp_001",
                    name="Reference competitor",
                    role="benchmark",
                    best_for="MVP validation",
                    supporting_evidence_ids=[evidence.evidence_id],
                )
            ],
            capability_boundaries=[
                CapabilityBoundary(
                    boundary_id="boundary_001",
                    title="Mock boundary",
                    description="The test runner avoids external network calls.",
                    boundary_type="short_term_feature",
                    supporting_evidence_ids=[evidence.evidence_id],
                )
            ],
            positioning_summary="The report is ready for frontend consumption.",
            recommendations=[
                Recommendation(
                    rec_id="rec_001",
                    title="Use the API payload",
                    content="Read report_data from the detail endpoint.",
                    priority="high",
                    rationale="The list endpoint intentionally omits heavy report data.",
                    supporting_evidence_ids=[evidence.evidence_id],
                )
            ],
        )
        report_data = ReportData(
            report_id=state["report_id"],
            topic=state["topic"],
            subject=state["subject"],
            subject_type=state["subject_type"],
            title=f"{state['subject']} Deep Research Report",
            overview=OverviewTabData(
                product_overview="API-generated test report.",
                key_findings=[
                    KeyFinding(
                        finding_id="finding_001",
                        title="Report generated",
                        content="The API returned a completed report.",
                        confidence="high",
                        supporting_evidence_ids=[evidence.evidence_id],
                    )
                ],
            ),
            vertical=vertical,
            horizontal=horizontal,
            quality_score=88,
            source_count=1,
            evidence_count=1,
            generated_at=evidence.retrieved_at,
        )
        quality_check = QualityCheckResult(
            quality_score=88,
            source_count=1,
            evidence_count=1,
        )
        artifacts = ReportFileStore(OUTPUT_DIR).write_report_artifacts(
            state["report_id"],
            report_data=report_data,
            evidence_cards=[evidence],
            raw_sources=[],
            run_log=[],
            quality_check=quality_check,
        )
        emit("persist_report_artifacts", "completed", "Saved report artifacts.")
        state.update(
            {
                "status": "completed",
                "progress_message": "Saved report artifacts.",
                "candidate_sources": [source],
                "evidence_cards": [evidence],
                "quality_check": quality_check,
                "report_data": report_data,
                "artifact_paths": artifacts,
            }
        )
        return state

    return run

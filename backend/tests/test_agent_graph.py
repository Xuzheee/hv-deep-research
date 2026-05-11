import shutil
from pathlib import Path

from app.agent.graph import NODE_SEQUENCE, run_report_graph, run_report_graph_observed
from app.agent.nodes.collect_info import MAX_TOOL_CALLS
from app.agent.schemas.report import ReportData


def test_report_graph_completes_and_writes_artifacts() -> None:
    output_dir = Path("backend/.test-output/agent-graph")
    shutil.rmtree(output_dir, ignore_errors=True)

    result = run_report_graph(
        {
            "report_id": "rpt_graph_test",
            "topic": "GPT-4o",
            "subject_type": "product",
            "reports_output_dir": str(output_dir),
        }
    )

    assert result["status"] == "completed"
    assert result["progress_message"] == "Saved report artifacts."
    assert result["tool_call_count"] <= MAX_TOOL_CALLS
    assert isinstance(result["report_data"], ReportData)
    assert result["report_data"].report_id == "rpt_graph_test"
    assert result["report_data"].overview.key_findings
    assert result["report_data"].narrative_report is not None
    assert result["report_data"].narrative_report.vertical_story
    assert result["report_data"].narrative_report.intersection_insights
    assert result["report_data"].vertical.stages[0].supporting_evidence_ids
    assert result["report_data"].horizontal.recommendations[0].supporting_evidence_ids
    assert result["quality_check"].quality_score == result["report_data"].quality_score

    report_dir = output_dir / "rpt_graph_test"
    assert (report_dir / "report_data.json").exists()
    assert (report_dir / "evidence_cards.json").exists()
    assert (report_dir / "raw_sources.json").exists()
    assert (report_dir / "run_log.json").exists()
    assert (report_dir / "quality_check.json").exists()

    shutil.rmtree(output_dir)


def test_graph_node_sequence_is_linear_mvp_path() -> None:
    assert NODE_SEQUENCE == [
        "initialize_report_run",
        "research_planner",
        "collect_info",
        "evidence_filter",
        "vertical_analysis",
        "horizontal_analysis",
        "synthesis_report_data",
        "quality_check",
        "persist_report_artifacts",
    ]


def test_observed_report_graph_emits_node_events() -> None:
    output_dir = Path("backend/.test-output/agent-graph-observed")
    shutil.rmtree(output_dir, ignore_errors=True)
    events: list[tuple[str, str, str]] = []

    result = run_report_graph_observed(
        {
            "report_id": "rpt_graph_observed_test",
            "topic": "GPT-4o",
            "subject_type": "product",
            "reports_output_dir": str(output_dir),
        },
        lambda node_name, status, message: events.append((node_name, status, message)),
    )

    assert result["status"] == "completed"
    assert events[0][0] == "initialize_report_run"
    assert events[0][1] == "running"
    assert events[-1][0] == "persist_report_artifacts"
    assert events[-1][1] == "completed"
    assert [event for event in events if event[0] == "synthesis_report_data"] == [
        ("synthesis_report_data", "running", "Synthesizing frontend-compatible report data."),
        ("synthesis_report_data", "completed", "Synthesized frontend-compatible report data."),
    ]
    assert {event[1] for event in events} == {"running", "completed"}

    shutil.rmtree(output_dir)

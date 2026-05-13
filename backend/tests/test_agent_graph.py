import shutil
from pathlib import Path

from app.agent import graph as graph_module
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
    assert result["report_data"].cross_insights
    assert result["report_data"].cross_insights[0].supporting_evidence_ids
    assert result["report_data"].vertical.stages[0].supporting_evidence_ids
    assert result["report_data"].horizontal.recommendations[0].supporting_evidence_ids
    assert result["quality_check"].quality_score == result["report_data"].quality_score

    report_dir = output_dir / "rpt_graph_test"
    assert (report_dir / "report_data.json").exists()
    assert (report_dir / "evidence_cards.json").exists()
    assert (report_dir / "raw_sources.json").exists()
    assert (report_dir / "run_log.json").exists()
    assert (report_dir / "quality_check.json").exists()
    assert (report_dir / "index.html").exists()
    assert result["artifact_paths"]["html_path"] == str(report_dir / "index.html")
    assert result["report_data"].title in (report_dir / "index.html").read_text(encoding="utf-8")

    shutil.rmtree(output_dir)


def test_graph_remediates_quality_once_before_persisting(monkeypatch) -> None:
    calls = {"synthesis_report_data": 0, "quality_check": 0}
    events: list[tuple[str, str, str]] = []

    def node(message: str):
        def run(state):
            return {**state, "progress_message": message}

        return run

    def synthesis_node(state):
        calls["synthesis_report_data"] += 1
        return {**state, "progress_message": "Synthesized frontend-compatible report data."}

    def quality_node(state):
        calls["quality_check"] += 1
        return {
            **state,
            "quality_check": type("Quality", (), {"quality_warning": True})(),
            "progress_message": "Completed report quality check.",
        }

    monkeypatch.setattr(
        graph_module,
        "NODE_FUNCTIONS",
        {
            "initialize_report_run": node("Initializing report run."),
            "research_planner": node("Planning research questions."),
            "collect_info": node("Collected notes."),
            "evidence_filter": node("Filtered evidence cards."),
            "vertical_analysis": node("Generated vertical analysis."),
            "horizontal_analysis": node("Generated horizontal analysis."),
            "cross_insights": node("Generated cross insights."),
            "synthesis_report_data": synthesis_node,
            "quality_check": quality_node,
            "quality_remediation": graph_module.quality_remediation,
            "persist_report_artifacts": node("Saved report artifacts."),
        },
    )

    result = graph_module.run_report_graph_observed({"run_log": []}, lambda *event: events.append(event))

    assert calls == {"synthesis_report_data": 2, "quality_check": 2}
    assert result["quality_remediation_attempted"] is True
    assert any(log["node"] == "quality_check" and "remediation" in log["message"] for log in result["run_log"])
    assert [event for event in events if event == ("quality_remediation", "completed", "Prepared one quality remediation pass.")] == [
        ("quality_remediation", "completed", "Prepared one quality remediation pass.")
    ]
    assert [event for event in events if event[0] == "persist_report_artifacts" and event[1] == "completed"] == [
        ("persist_report_artifacts", "completed", "Saved report artifacts.")
    ]


def test_initialize_report_run_resets_remediation_state() -> None:
    result = graph_module.initialize_report_run(
        {
            "topic": "GPT-4o",
            "subject_type": "product",
            "quality_remediation_attempted": True,
        }
    )

    assert result["quality_remediation_attempted"] is False


def test_graph_node_sequence_is_linear_mvp_path() -> None:
    assert NODE_SEQUENCE == [
        "initialize_report_run",
        "research_planner",
        "collect_info",
        "evidence_filter",
        "vertical_analysis",
        "horizontal_analysis",
        "cross_insights",
        "synthesis_report_data",
        "quality_check",
        "quality_remediation",
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
    assert [event for event in events if event[0] == "cross_insights"] == [
        ("cross_insights", "running", "Generating cross insights."),
        ("cross_insights", "completed", "Generated cross insights."),
    ]
    assert [event for event in events if event[0] == "synthesis_report_data"] == [
        ("synthesis_report_data", "running", "Synthesizing frontend-compatible report data."),
        ("synthesis_report_data", "completed", "Synthesized frontend-compatible report data."),
        ("synthesis_report_data", "running", "Synthesizing frontend-compatible report data."),
        ("synthesis_report_data", "completed", "Synthesized frontend-compatible report data."),
    ]
    assert [event for event in events if event[0] == "quality_remediation"] == [
        ("quality_remediation", "running", "Preparing one quality remediation pass."),
        ("quality_remediation", "completed", "Prepared one quality remediation pass."),
    ]
    assert {event[1] for event in events} == {"running", "completed"}

    shutil.rmtree(output_dir)

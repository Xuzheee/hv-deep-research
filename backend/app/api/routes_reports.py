from collections.abc import Callable

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.graph import run_report_graph, run_report_graph_observed
from app.agent.state import ReportAgentState
from app.api.schemas import CreateReportRequest, HistoryReport, ReportDetail, ReportStatusResponse
from app.config import settings
from app.db.repository import ReportRepository
from app.db.session import SessionLocal, get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])

ReportRunner = Callable[..., ReportAgentState]
_report_runner: ReportRunner = run_report_graph_observed

NODE_REPORT_STATUS = {
    "initialize_report_run": "planning",
    "research_planner": "planning",
    "collect_info": "searching",
    "evidence_filter": "filtering",
    "vertical_analysis": "analyzing_vertical",
    "horizontal_analysis": "analyzing_horizontal",
    "cross_insights": "synthesizing",
    "synthesis_report_data": "synthesizing",
    "quality_check": "quality_checking",
    "quality_remediation": "synthesizing",
    "persist_report_artifacts": "persisting",
}


def set_report_runner(runner: ReportRunner) -> None:
    global _report_runner
    _report_runner = runner


def reset_report_runner() -> None:
    set_report_runner(run_report_graph_observed)


def get_repository(db: Session = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db, reports_output_dir=settings.reports_output_dir)


@router.post("", response_model=ReportDetail)
def create_report(
    request: CreateReportRequest,
    background_tasks: BackgroundTasks,
    repository: ReportRepository = Depends(get_repository),
) -> ReportDetail:
    report = repository.create_report(topic=request.topic, subject_type=request.subject_type)
    repository.insert_event(report.report_id, "create_report", "pending", "Report queued.")
    background_tasks.add_task(run_report_background, report.report_id)
    return ReportDetail(report=repository.to_history_report(repository.get_report(report.report_id)))


@router.get("", response_model=list[HistoryReport])
def list_reports(repository: ReportRepository = Depends(get_repository)) -> list[HistoryReport]:
    return [repository.to_history_report(report) for report in repository.list_reports()]


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: str, repository: ReportRepository = Depends(get_repository)) -> ReportDetail:
    report = repository.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetail(report=repository.to_history_report(report, include_report_data=True))


@router.get("/{report_id}/status", response_model=ReportStatusResponse)
def get_report_status(
    report_id: str,
    repository: ReportRepository = Depends(get_repository),
) -> ReportStatusResponse:
    report = repository.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    history = repository.to_history_report(report)
    return ReportStatusResponse(
        report_id=history.report_id,
        status=history.status,
        progress_message=history.progress_message,
        progress_steps=history.progress_steps,
        error_message=history.error_message,
    )


def run_report_background(report_id: str) -> None:
    db = SessionLocal()
    repository = ReportRepository(db, reports_output_dir=settings.reports_output_dir)
    try:
        report = repository.get_report(report_id)
        if report is None:
            return

        def record_node_event(node_name: str, event_status: str, message: str) -> None:
            if event_status == "running":
                repository.update_status(report_id, NODE_REPORT_STATUS[node_name], message)
            elif event_status == "failed":
                repository.update_status(report_id, "failed", "Report generation failed.", error_message=message)
            repository.insert_event(report_id, node_name, event_status, message)

        repository.update_status(report_id, "planning", "Starting research plan.")
        initial_state = {
            "report_id": report.report_id,
            "topic": report.topic,
            "subject": report.subject or report.topic,
            "subject_type": report.subject_type or "other",
            "reports_output_dir": settings.reports_output_dir,
        }
        if _report_runner is run_report_graph:
            result = run_report_graph_observed(initial_state, record_node_event)
        else:
            result = _report_runner(initial_state, record_node_event)
        repository.complete_from_graph_state(report_id, result)
    except Exception as exc:
        repository.update_status(report_id, "failed", "Report generation failed.", error_message=str(exc))
        repository.insert_event(report_id, "research", "failed", str(exc))
    finally:
        db.close()

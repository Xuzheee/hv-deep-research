import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.agent.schemas.report import ReportData
from app.agent.state import ReportAgentState
from app.api.schemas import HistoryReport, ProgressStep
from app.db.models import Report, RunEvent


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ReportRepository:
    def __init__(self, db: Session, reports_output_dir: str = "backend/app/outputs/reports") -> None:
        self.db = db
        self.reports_output_dir = Path(reports_output_dir)

    def create_report(self, topic: str, subject_type: str, subject: str | None = None) -> Report:
        now = utc_now()
        report_id = f"rpt_{uuid4().hex}"
        report = Report(
            report_id=report_id,
            topic=topic,
            subject=subject or topic,
            subject_type=subject_type,
            status="pending",
            progress_message="Waiting to start research.",
            quality_warning=False,
            report_dir=str(self.reports_output_dir / report_id),
            created_at=now,
            updated_at=now,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: str) -> Report | None:
        return self.db.scalar(
            select(Report)
            .where(Report.report_id == report_id)
            .options(selectinload(Report.events))
            .execution_options(populate_existing=True)
        )

    def list_reports(self) -> list[Report]:
        return list(
            self.db.scalars(
                select(Report).options(selectinload(Report.events)).order_by(Report.created_at.desc())
            )
        )

    def update_status(
        self,
        report_id: str,
        status: str,
        progress_message: str | None = None,
        error_message: str | None = None,
    ) -> Report:
        report = self._require_report(report_id)
        report.status = status
        report.updated_at = utc_now()
        if progress_message is not None:
            report.progress_message = progress_message
        if error_message is not None:
            report.error_message = error_message
        self.db.commit()
        self.db.refresh(report)
        return report

    def insert_event(
        self,
        report_id: str,
        step: str,
        status: str,
        message: str | None = None,
        payload: dict | None = None,
    ) -> RunEvent:
        self._require_report(report_id)
        event = RunEvent(
            event_id=f"evt_{uuid4().hex}",
            report_id=report_id,
            step=step,
            status=status,
            message=message,
            payload_json=json.dumps(payload) if payload is not None else None,
            created_at=utc_now(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_artifact_paths(
        self,
        report_id: str,
        *,
        report_data_path: str | None = None,
        evidence_cards_path: str | None = None,
        raw_sources_path: str | None = None,
        run_log_path: str | None = None,
        quality_check_path: str | None = None,
    ) -> Report:
        report = self._require_report(report_id)
        report.report_data_path = report_data_path if report_data_path is not None else report.report_data_path
        report.evidence_cards_path = (
            evidence_cards_path if evidence_cards_path is not None else report.evidence_cards_path
        )
        report.raw_sources_path = raw_sources_path if raw_sources_path is not None else report.raw_sources_path
        report.run_log_path = run_log_path if run_log_path is not None else report.run_log_path
        report.quality_check_path = quality_check_path if quality_check_path is not None else report.quality_check_path
        report.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(report)
        return report

    def complete_from_graph_state(self, report_id: str, state: ReportAgentState) -> Report:
        report = self._require_report(report_id)
        artifact_paths = state.get("artifact_paths", {})
        report.status = state.get("status", "completed")
        report.progress_message = state.get("progress_message", "Report completed.")
        report.report_data_path = artifact_paths.get("report_data_path", report.report_data_path)
        report.evidence_cards_path = artifact_paths.get("evidence_cards_path", report.evidence_cards_path)
        report.raw_sources_path = artifact_paths.get("raw_sources_path", report.raw_sources_path)
        report.run_log_path = artifact_paths.get("run_log_path", report.run_log_path)
        report.quality_check_path = artifact_paths.get("quality_check_path", report.quality_check_path)
        report.source_count = len(state.get("candidate_sources", []))
        report.evidence_count = len(state.get("evidence_cards", []))
        if "quality_check" in state:
            report.quality_score = state["quality_check"].quality_score
            report.quality_warning = state["quality_check"].quality_warning
        report.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(report)
        return report

    def to_history_report(self, report: Report, include_report_data: bool = False) -> HistoryReport:
        return HistoryReport(
            report_id=report.report_id,
            topic=report.topic,
            subject_type=report.subject_type or "other",
            status=report.status,
            quality_warning=report.quality_warning,
            quality_score=report.quality_score,
            created_at=report.created_at,
            updated_at=report.updated_at,
            error_message=report.error_message,
            report_data=self._load_report_data(report) if include_report_data else None,
            progress_steps=[self._event_to_progress_step(event) for event in report.events],
            progress_message=report.progress_message or "",
        )

    def _require_report(self, report_id: str) -> Report:
        report = self.get_report(report_id)
        if report is None:
            raise ValueError(f"Report not found: {report_id}")
        return report

    def _load_report_data(self, report: Report) -> ReportData | None:
        if report.report_data_path is None:
            return None
        path = Path(report.report_data_path)
        if not path.exists():
            return None
        return ReportData.model_validate_json(path.read_text(encoding="utf-8"))

    def _event_to_progress_step(self, event: RunEvent) -> ProgressStep:
        return ProgressStep(
            step_id=event.event_id,
            label=event.step,
            status=event.status,
            message=event.message,
            timestamp=event.created_at,
        )

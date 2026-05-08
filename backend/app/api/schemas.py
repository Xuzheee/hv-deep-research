from pydantic import BaseModel, Field

from app.agent.schemas.report import ReportData, SubjectType

ReportStatus = str


class ProgressStep(BaseModel):
    step_id: str
    label: str
    status: str
    message: str | None = None
    timestamp: str | None = None


class CreateReportRequest(BaseModel):
    topic: str = Field(min_length=1)
    subject_type: SubjectType
    force_refresh: bool = False


class HistoryReport(BaseModel):
    report_id: str
    topic: str
    subject_type: SubjectType
    status: ReportStatus
    quality_warning: bool
    quality_score: int | None
    created_at: str
    updated_at: str
    error_message: str | None
    report_data: ReportData | None = None
    progress_steps: list[ProgressStep] = Field(default_factory=list)
    progress_message: str


class ReportDetail(BaseModel):
    report: HistoryReport


class ReportStatusResponse(BaseModel):
    report_id: str
    status: ReportStatus
    progress_message: str
    progress_steps: list[ProgressStep] = Field(default_factory=list)
    error_message: str | None = None

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[str] = mapped_column(String, primary_key=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    subject_type: Mapped[str | None] = mapped_column(String)
    focus: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, nullable=False)
    progress_message: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    quality_score: Mapped[int | None] = mapped_column(Integer)
    quality_warning: Mapped[bool] = mapped_column(Boolean, default=False)
    report_dir: Mapped[str] = mapped_column(Text, nullable=False)
    report_data_path: Mapped[str | None] = mapped_column(Text)
    html_path: Mapped[str | None] = mapped_column(Text)
    evidence_cards_path: Mapped[str | None] = mapped_column(Text)
    raw_sources_path: Mapped[str | None] = mapped_column(Text)
    run_log_path: Mapped[str | None] = mapped_column(Text)
    quality_check_path: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(Text)
    source_count: Mapped[int | None] = mapped_column(Integer)
    evidence_count: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)

    events: Mapped[list["RunEvent"]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="RunEvent.created_at",
    )


class RunEvent(Base):
    __tablename__ = "run_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.report_id"), nullable=False)
    step: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    payload_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    report: Mapped[Report] = relationship(back_populates="events")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Report
from app.db.repository import ReportRepository
from app.db.session import Base


def make_repository() -> ReportRepository:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return ReportRepository(session_factory(), reports_output_dir="test-output/reports")


def test_repository_creates_report() -> None:
    repository = make_repository()

    report = repository.create_report(topic="GPT-4o", subject_type="product")

    assert report.report_id.startswith("rpt_")
    assert report.topic == "GPT-4o"
    assert report.subject == "GPT-4o"
    assert report.status == "pending"
    assert report.report_dir.endswith(report.report_id)


def test_repository_updates_status_and_events() -> None:
    repository = make_repository()
    report = repository.create_report(topic="Claude", subject_type="product")

    updated = repository.update_status(
        report.report_id,
        "planning",
        progress_message="Planning research questions.",
    )
    event = repository.insert_event(
        report.report_id,
        step="research_planner",
        status="completed",
        message="Plan ready.",
        payload={"queries": 3},
    )
    fetched = repository.get_report(report.report_id)

    assert updated.status == "planning"
    assert updated.progress_message == "Planning research questions."
    assert event.payload_json == '{"queries": 3}'
    assert fetched is not None
    assert fetched.events[0].step == "research_planner"


def test_repository_updates_artifact_paths_and_lists_history() -> None:
    repository = make_repository()
    older = repository.create_report(topic="Firecrawl", subject_type="technology")
    newer = repository.create_report(topic="Tavily", subject_type="technology")

    repository.update_artifact_paths(
        older.report_id,
        report_data_path="reports/old/report_data.json",
        evidence_cards_path="reports/old/evidence_cards.json",
        raw_sources_path="reports/old/raw_sources.json",
        run_log_path="reports/old/run_log.json",
        quality_check_path="reports/old/quality_check.json",
    )
    reports = repository.list_reports()
    history_item = repository.to_history_report(repository.get_report(older.report_id))

    assert [report.report_id for report in reports] == [newer.report_id, older.report_id]
    assert repository.get_report(older.report_id).report_data_path == "reports/old/report_data.json"
    assert repository.get_report(older.report_id).quality_check_path == "reports/old/quality_check.json"
    assert history_item.report_id == older.report_id
    assert history_item.subject_type == "technology"
    assert history_item.report_data is None


def test_repository_raises_for_missing_report() -> None:
    repository = make_repository()

    try:
        repository.update_status("missing", "failed")
    except ValueError as exc:
        assert "Report not found" in str(exc)
    else:
        raise AssertionError("Missing report update did not raise ValueError")


def test_models_define_reports_and_run_events_tables() -> None:
    assert Report.__tablename__ == "reports"

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class ReportFileStore:
    def __init__(self, base_dir: str | Path = "backend/app/outputs/reports") -> None:
        self.base_dir = Path(base_dir)

    def report_dir(self, report_id: str) -> Path:
        return self.base_dir / report_id

    def write_json(self, report_id: str, filename: str, data: Any) -> str:
        path = self.report_dir(report_id) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self._jsonable(data), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(path)

    def read_json(self, report_id: str, filename: str) -> Any:
        path = self.report_dir(report_id) / filename
        return json.loads(path.read_text(encoding="utf-8"))

    def write_report_artifacts(
        self,
        report_id: str,
        *,
        report_data: Any,
        evidence_cards: Any,
        raw_sources: Any,
        run_log: Any,
        quality_check: Any,
    ) -> dict[str, str]:
        return {
            "report_data_path": self.write_json(report_id, "report_data.json", report_data),
            "evidence_cards_path": self.write_json(report_id, "evidence_cards.json", evidence_cards),
            "raw_sources_path": self.write_json(report_id, "raw_sources.json", raw_sources),
            "run_log_path": self.write_json(report_id, "run_log.json", run_log),
            "quality_check_path": self.write_json(report_id, "quality_check.json", quality_check),
        }

    def _jsonable(self, data: Any) -> Any:
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")
        if isinstance(data, list):
            return [self._jsonable(item) for item in data]
        if isinstance(data, dict):
            return {key: self._jsonable(value) for key, value in data.items()}
        return data

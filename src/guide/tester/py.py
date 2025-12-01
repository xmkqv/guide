"""Python tester: parse pytest results and extract signals."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from _pytest.reports import pytest_report_from_serializable
from pydantic import BaseModel, ConfigDict
from pytest import CollectReport, TestReport

from guide.lang import Lang
from guide.signal import Test, gen_timestamp

type Report = TestReport | CollectReport

if TYPE_CHECKING:
    from guide.mission import Mission


class Tester(BaseModel):
    model_config = ConfigDict(frozen=True)

    lang: Literal[Lang.Py] = Lang.Py
    results_path_stem: str = "results/results.jsonl"

    def get_signal(self, mission: "Mission") -> list[Test]:
        results_path = mission.dir / self.results_path_stem
        if not results_path.exists():
            return []

        reports = _filter_test_reports(_load_reportlog(results_path))
        return [self._report_to_test(r, idx) for idx, r in enumerate(reports)]

    def _report_to_test(self, report: "TestReport", idx: int) -> Test:
        return Test(
            id=f"T{idx}",
            ref=report.nodeid,
            args={},
            data={
                "outcome": report.outcome,
                "duration": report.duration,
                "timestamp": gen_timestamp(),
            },
        )


def _load_reportlog(path: Path) -> Iterator[Report]:
    """Load pytest-reportlog JSONL file, yielding typed report objects."""
    for lineno, line in enumerate(path.open(), start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {e}") from e
        report_type = obj.get("$report_type")
        if report_type in ("TestReport", "CollectReport"):
            report = pytest_report_from_serializable(obj)
            if report is not None:
                yield report


def _filter_test_reports(reports: Iterator[Report]) -> Iterator[TestReport]:
    """Filter to TestReport objects from the call phase only."""
    for report in reports:
        if isinstance(report, TestReport) and report.when == "call":
            yield report

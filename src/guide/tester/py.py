"""Python tester: parse pytest results and extract signals."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from _pytest.reports import pytest_report_from_serializable
from pydantic import BaseModel, ConfigDict
from pytest import CollectReport, TestReport

from guide import signal
from guide.lang import Lang

if TYPE_CHECKING:
    from guide.mission import Mission

type Report = TestReport | CollectReport


class Tester(BaseModel):
    model_config = ConfigDict(frozen=True)

    lang: Literal[Lang.Py] = Lang.Py
    results_path_stem: str = "results/results.jsonl"
    include_unlinked: bool = False

    def get_signal(self, mission: Mission) -> list[signal.Test]:
        results_path = mission.dir / self.results_path_stem
        if not results_path.exists():
            return []

        reports = _filter_test_reports(_load_reportlog(results_path))
        tests = [
            self._report_to_test(r, idx, mission.dir)
            for idx, r in enumerate(reports)
        ]

        if self.include_unlinked:
            return tests
        return [t for t in tests if t.spec_ids]

    def _report_to_test(
        self, report: TestReport, idx: int, base_dir: Path
    ) -> signal.Test:
        docstring = _get_test_docstring(report.nodeid, base_dir)
        spec_ids = signal.parse_design_ids(docstring)

        return signal.Test(
            id=f"T{idx}",
            ref=report.nodeid,
            spec_ids=spec_ids,
            result={
                "outcome": report.outcome,
                "duration": report.duration,
                "timestamp": signal.gen_timestamp(),
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


def _get_test_docstring(nodeid: str, base_dir: Path) -> str | None:
    """Extract docstring from test function via nodeid.

    Nodeid format: path/to/test_file.py::TestClass::test_method
    or: path/to/test_file.py::test_function
    """
    try:
        file_part, *rest = nodeid.split("::")
        if not rest:
            return None

        file_path = base_dir / file_part
        if not file_path.exists():
            return None

        module = _load_module_from_path(file_path)
        if module is None:
            return None

        obj = module
        for part in rest:
            # Handle parameterized tests: test_func[param] -> test_func
            name = part.split("[")[0]
            obj = getattr(obj, name, None)
            if obj is None:
                return None

        return obj.__doc__
    except (AttributeError, ImportError, OSError, TypeError):
        return None


def _load_module_from_path(path: Path) -> object | None:
    """Dynamically load a Python module from file path."""
    try:
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except (ImportError, OSError, SyntaxError, TypeError, ValueError):
        return None

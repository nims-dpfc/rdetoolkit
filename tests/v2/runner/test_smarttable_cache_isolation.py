"""Regression tests for run-scoped SmartTable base-invoice caching.

Equivalence partitions (EP):

| API | Partition | Rationale | Expected | Test ID |
| --- | --- | --- | --- | --- |
| ``Runner.run`` | same source path, changed content | stale process cache | second run uses changed content | TC-G0-CACHE-001 |

Boundary values (BV):

| API | Boundary | Rationale | Expected | Test ID |
| --- | --- | --- | --- | --- |
| ``Runner.run`` | two consecutive runs | minimum cross-run sequence | cache is isolated at run boundary | TC-G0-CACHE-001 |

NOTE (2026-07-15): reconstructed from the surviving pytest ``.pyc`` after the
original working tree was wiped before commit (see session_g0.md). Semantics,
test ids and assertions are preserved from the verified original.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest

from rdetoolkit.domain.invoice import build_smarttable_tile_invoice
from rdetoolkit.processing.processors.invoice import SmartTableInvoiceInitializer
from rdetoolkit.report.run_report import RunReport
from rdetoolkit.runner.lifecycle import Runner
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.types import RdeConfig

_OWNER_ID = "0" * 56

_INVOICE_SCHEMA: dict[str, Any] = {
    "required": ["sample"],
    "properties": {
        "sample": {
            "type": "object",
            "label": {"ja": "サンプル", "en": "Sample"},
            "properties": {},
        },
    },
}


class _SmartTableProbeRunner(Runner):
    """Run the real SmartTable invoice builder through the Runner boundary."""

    def load_config(self, overrides: dict[str, Any] | None = None) -> RdeConfig:
        return RdeConfig()

    def resolve_mode(self, config: RdeConfig) -> ModeKind:
        return ModeKind.smarttable

    def pre_validate(self, config: RdeConfig) -> None:
        return None

    def iterate(
        self,
        flow_fn: Callable[..., Any],
        mode: ModeKind,
        config: RdeConfig,
    ) -> RunReport:
        data_root = self.root / "data"
        build_smarttable_tile_invoice(
            smarttable_rowfile=data_root / "inputdata" / "fsmarttable_row_0.csv",
            invoice_org=data_root / "invoice" / "invoice.json",
            invoice_schema_path=data_root / "tasksupport" / "invoice.schema.json",
            dist_path=data_root / "output" / "invoice" / "invoice.json",
        )
        return RunReport(
            run_id=self.run_id,
            status="success",
            flow_id="tests.smarttable_probe",
            mode=mode.value,
            started_at="2026-07-15T00:00:00",
            duration_ms=0.0,
            config_digest="sha256:test",
            iterations=[],
            warnings=[],
        )

    def post_validate(self, config: RdeConfig, report: RunReport) -> None:
        return None

    def finalize(self, report: RunReport, config: RdeConfig) -> None:
        return None


@pytest.fixture()
def isolated_smarttable_cache() -> Generator[None, None, None]:
    """Prevent this process-global regression fixture leaking to other tests."""
    SmartTableInvoiceInitializer.clear_base_invoice_cache()
    yield
    SmartTableInvoiceInitializer.clear_base_invoice_cache()


def _write_source_invoice(path: Path, data_name: str) -> None:
    payload = {
        "datasetId": "seed-dataset",
        "basic": {
            "dateSubmitted": "2026-07-15",
            "dataOwnerId": _OWNER_ID,
            "dataName": data_name,
        },
        "sample": {"sampleId": "00000000-0000-0000-0000-000000000001"},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_changed_base_invoice_is_reloaded_on_second_run__tc_g0_cache_001(
    tmp_path: Path,
    isolated_smarttable_cache: None,
) -> None:
    """TC-G0-CACHE-001: each run reads a fresh SmartTable base invoice."""
    # Given: a data tree whose base invoice.json changes between two runs
    data_root = tmp_path / "data"
    (data_root / "inputdata").mkdir(parents=True)
    (data_root / "invoice").mkdir()
    (data_root / "tasksupport").mkdir()
    row_path = data_root / "inputdata" / "fsmarttable_row_0.csv"
    row_path.write_text("basic/dateSubmitted\n2026-07-15\n", encoding="utf-8")
    (data_root / "tasksupport" / "invoice.schema.json").write_text(
        json.dumps(_INVOICE_SCHEMA),
        encoding="utf-8",
    )

    source_path = data_root / "invoice" / "invoice.json"
    _write_source_invoice(source_path, "first-run")

    # When: two consecutive same-process runs read the same source path
    first_report = _SmartTableProbeRunner(root=tmp_path).run(lambda: None)
    _write_source_invoice(source_path, "second-run")
    second_report = _SmartTableProbeRunner(root=tmp_path).run(lambda: None)
    generated = json.loads(
        (data_root / "output" / "invoice" / "invoice.json").read_text(encoding="utf-8"),
    )

    # Then: the second run must observe the changed base invoice, not a stale
    # process-global cache entry left behind by the first run.
    assert first_report.status == "success"
    assert second_report.status == "success"
    assert generated["basic"]["dataName"] == "second-run"

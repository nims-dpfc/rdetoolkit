"""Runner integration contracts for Phase H3 domain services.

Equivalence partitions (EP):

| API | Partition | Expected | Test ID |
| --- | --- | --- | --- |
| ``RunPlanner.create`` | injected invoice service | starts run-owned service | TC-H3-INT-001 |
| ``RunPlanner`` | invalid implicit global service | no process-wide cache clear | TC-H3-INT-002 |

Boundary values (BV):

| API | Boundary | Expected | Test ID |
| --- | --- | --- | --- |
| ``RunPlanner.create`` | zero tiles (lazy plan) | service starts before enumeration | TC-H3-INT-003 |
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdetoolkit.api.request import FlowTarget, RunRequest
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.planner import RunPlanner
from rdetoolkit.types import RdeConfig


class _InvoiceServiceProbe:
    """Record the run boundary without touching invoice files."""

    def __init__(self) -> None:
        self.roots: list[Path] = []

    def begin_run(self, root: Path) -> None:
        self.roots.append(root)

    def invariant_invoice(self, mode: ModeKind, *, root: Path) -> None:
        return None

    def backup(self, mode: ModeKind, **kwargs: Any) -> Path:
        return Path(kwargs["root"]) / "invoice" / "invoice.json"

    def prepare_tile(self, mode: ModeKind, **kwargs: Any) -> None:
        return None


def test_planner_starts_injected_invoice_service_before_lazy_iteration__tc_h3_int_001_003(
    tmp_path: Path,
) -> None:
    """TC-H3-INT-001/003: each plan owns an explicitly started invoice service."""
    # Given: a planner with an injected service and a root whose tiles stay lazy
    service = _InvoiceServiceProbe()
    planner = RunPlanner(
        inputdata_path=tmp_path / "inputdata",
        unpacked_dir_path=tmp_path / "temp",
        run_id_factory=lambda: "h3-run",
        invoice_service=service,
    )
    request = RunRequest(root=tmp_path, target=FlowTarget(function=lambda: None))

    # When: creating, but not enumerating, an execution plan
    plan = planner.create(request, config=RdeConfig(), mode=ModeKind.invoice)

    # Then: the service is scoped at the run boundary before lazy tile access
    assert plan.run_id == "h3-run"
    assert service.roots == [tmp_path]

"""Phase H contract for ``RunReport.to_legacy_statuses()``.

EP table:

| RunReport mode | Frozen v1 oracle | Expected | Test ID |
|---|---|---|---|
| invoice | ``v1/invoice/ok.json`` | exact legacy-return JSON | TC-EP-G2-301 |
| excelinvoice | ``v1/excelinvoice/ok.json`` | exact legacy-return JSON | TC-EP-G2-302 |
| multidatatile | ``v1/multidatatile/ok.json`` | exact legacy-return JSON | TC-EP-G2-303 |
| smarttable | ``v1/smarttable/ok.json`` | exact legacy-return JSON | TC-EP-G2-304 |
| rdeformat | ``v1/rdeformat/ok.json`` | exact legacy-return JSON | TC-EP-G2-305 |

BV table:

| Boundary | Expected | Covered by |
|---|---|---|
| one status | full single-item ``statuses`` list | invoice cell |
| multiple statuses | order and every field preserved | other four cells |
"""

import json
from pathlib import Path
from typing import Any

import pytest


_EXPECTED_ROOT = Path(__file__).parent / "fixtures" / "expected" / "v1"


@pytest.mark.xfail(
    strict=False,
    reason="Phase H: RunReport.to_legacy_statuses() is not implemented yet",
)
@pytest.mark.parametrize(
    "mode,test_id",
    [
        pytest.param("invoice", "TC-EP-G2-301", id="invoice"),
        pytest.param("excelinvoice", "TC-EP-G2-302", id="excelinvoice"),
        pytest.param("multidatatile", "TC-EP-G2-303", id="multidatatile"),
        pytest.param("smarttable", "TC-EP-G2-304", id="smarttable"),
        pytest.param("rdeformat", "TC-EP-G2-305", id="rdeformat"),
    ],
)
def test_to_legacy_statuses_matches_frozen_v1_ok_payload(
    mode: str,
    test_id: str,
) -> None:
    """TC-EP-G2-301..305: Each mode matches its frozen v1 return JSON."""
    from rdetoolkit.report.run_report import RunReport

    # Given: the G1-frozen v1 return and a RunReport for that same scenario
    fixture: dict[str, Any] = json.loads(
        (_EXPECTED_ROOT / mode / "ok.json").read_text(encoding="utf-8")
    )
    expected = fixture["observed"]["legacy_return"]
    report = RunReport(
        run_id="<RUN_ID>",
        status="success",
        flow_id="legacy:custom_dataset_function",
        mode=mode,
        started_at="<DATE>",
        duration_ms=0.0,
        config_digest="sha256:<NORMALIZED>",
        iterations=expected["statuses"],
        warnings=[],
    )

    # When: requesting the explicit legacy compatibility representation
    actual_json = report.to_legacy_statuses()

    # Then: it is a JSON string matching every frozen field and value
    assert test_id.startswith("TC-EP-G2-3")
    assert isinstance(actual_json, str)
    assert json.loads(actual_json) == expected

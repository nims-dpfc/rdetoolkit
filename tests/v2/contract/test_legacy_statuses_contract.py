"""Phase H contract for ``RunReport.to_legacy_statuses()``.

EP table:

| RunReport mode | Frozen v1 oracle | Expected | Test ID |
|---|---|---|---|
| invoice | ``v1/invoice/ok.json`` | exact legacy-return JSON | TC-EP-G2-301 |
| excelinvoice | ``v1/excelinvoice/ok.json`` | exact legacy-return JSON | TC-EP-G2-302 |
| multidatatile | ``v1/multidatatile/ok.json`` | exact legacy-return JSON | TC-EP-G2-303 |
| smarttable | ``v1/smarttable/ok.json`` | exact legacy-return JSON | TC-EP-G2-304 |
| rdeformat | ``v1/rdeformat/ok.json`` | exact legacy-return JSON | TC-EP-G2-305 |
| each mode | ``usererr.json`` | total failed-run conversion | TC-EP-GR2-306..310 |
| each mode | ``valerr.json`` | total failed-run conversion | TC-EP-GR2-311..315 |

BV table:

| Boundary | Expected | Covered by |
|---|---|---|
| one status | full single-item ``statuses`` list | invoice cell |
| multiple statuses | order and every field preserved | other four cells |
| null v1 error return | v2 defines one structural failed status | ten error seats |
"""

import json
from pathlib import Path
from typing import Any

import pytest


_EXPECTED_ROOT = Path(__file__).parent / "fixtures" / "expected" / "v1"


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
        (_EXPECTED_ROOT / mode / "ok.json").read_text(encoding="utf-8"),
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


@pytest.mark.parametrize(
    ("mode", "outcome", "test_id"),
    [
        pytest.param(mode, outcome, f"TC-EP-GR2-{306 + index}", id=f"{mode}-{outcome}")
        for index, (mode, outcome) in enumerate(
            (mode, outcome)
            for outcome in ("usererr", "valerr")
            for mode in ("invoice", "excelinvoice", "multidatatile", "smarttable", "rdeformat")
        )
    ],
)
def test_to_legacy_statuses_matches_frozen_v1_error_payload(
    mode: str,
    outcome: str,
    test_id: str,
) -> None:
    """TC-EP-GR2-306..315: Error seats follow each frozen v1 return contract."""
    # Given: the frozen v1 error result for one mode/outcome seat
    fixture: dict[str, Any] = json.loads(
        (_EXPECTED_ROOT / mode / f"{outcome}.json").read_text(encoding="utf-8"),
    )
    observed = fixture["observed"]
    expected = observed["legacy_return"]
    from rdetoolkit.report.run_report import RunReport

    if expected is None:
        ok_fixture: dict[str, Any] = json.loads(
            (_EXPECTED_ROOT / mode / "ok.json").read_text(encoding="utf-8"),
        )
        reference_status = ok_fixture["observed"]["legacy_return"]["statuses"][0]
        job_failed_text = observed["job_failed_text"]
        code_line, message_text = job_failed_text.split("\n", maxsplit=1)
        status = {
            **reference_status,
            "error_code": int(code_line.removeprefix("ErrorCode=")),
            "error_message": message_text.removeprefix("ErrorMessage=").rstrip("\n"),
            "status": "failed",
        }
        iterations = [status]
    else:
        iterations = expected["statuses"]

    report = RunReport(
        run_id="<RUN_ID>",
        status="failed",
        flow_id="legacy:custom_dataset_function",
        mode=mode,
        started_at="<DATE>",
        duration_ms=0.0,
        config_digest="sha256:<NORMALIZED>",
        iterations=iterations,
        warnings=[],
    )

    # When: converting the future unified failed report to the legacy shape
    actual_json = report.to_legacy_statuses()

    # Then: non-null v1 returns match exactly, while formerly unobservable
    # failed returns preserve the frozen field shape and job.failed values
    assert test_id.startswith("TC-EP-GR2-3")
    assert isinstance(actual_json, str)
    actual = json.loads(actual_json)
    if expected is not None:
        assert actual == expected
        return
    actual_statuses = actual["statuses"]
    assert len(actual_statuses) == len(report.iterations)
    assert set(actual_statuses[0]) == set(reference_status)
    assert actual_statuses[0]["error_code"] == status["error_code"]
    assert actual_statuses[0]["error_message"] == status["error_message"]

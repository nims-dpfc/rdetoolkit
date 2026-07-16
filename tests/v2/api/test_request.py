"""Contract tests for public run-request normalization.

EP table:

| API | Partition | Expected | Test ID |
|---|---|---|---|
| ``build_run_request`` | flow only | ``FlowTarget`` | TC-EP-G2-101 |
| ``build_run_request`` | callback only | ``LegacyCallbackTarget`` | TC-EP-G2-102 |
| ``build_run_request`` | both entry points | E1001 with remediation | TC-EP-G2-103 |
| ``build_run_request`` | config/root/options supplied | values retained | TC-EP-G2-104 |
| request dataclasses | field mutation | ``FrozenInstanceError`` | TC-EP-G2-105 |
| request dataclasses | undeclared attribute | ``TypeError`` from frozen slots | TC-EP-G2-106 |

BV table:

| API | Boundary | Expected | Test ID |
|---|---|---|---|
| ``build_run_request`` | neither entry point supplied | legacy target containing ``None`` | TC-BV-G2-101 |
| ``build_run_request`` | root omitted | current working directory captured | TC-BV-G2-102 |
"""

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from rdetoolkit.api.request import (
    FlowTarget,
    LegacyCallbackTarget,
    RunRequest,
    build_run_request,
)
from rdetoolkit.errors import ERROR_CATALOG, RdeConfigError


def _flow() -> None:
    return None


def _callback(_src: object, _out: object) -> None:
    return None


def test_flow_only_normalizes_to_flow_target__tc_ep_g2_101() -> None:
    """TC-EP-G2-101: A flow is wrapped in a FlowTarget."""
    # Given: only a v2 flow entry point
    # When: normalizing the public API request
    request = build_run_request(flow=_flow, custom_dataset_function=None, config=None)

    # Then: the callable is preserved verbatim in a FlowTarget
    assert isinstance(request.target, FlowTarget)
    assert request.target.function is _flow


def test_callback_only_normalizes_to_legacy_target__tc_ep_g2_102() -> None:
    """TC-EP-G2-102: A callback is wrapped in a LegacyCallbackTarget."""
    # Given: only a legacy callback entry point
    # When: normalizing the public API request
    request = build_run_request(
        flow=None,
        custom_dataset_function=_callback,
        config=None,
    )

    # Then: the callable is preserved verbatim in a legacy target
    assert isinstance(request.target, LegacyCallbackTarget)
    assert request.target.function is _callback


def test_both_entry_points_raise_catalog_e1001__tc_ep_g2_103() -> None:
    """TC-EP-G2-103: Supplying both entry points raises catalog error 1001."""
    # Given: both mutually exclusive entry points
    # When / Then: normalization fails with the existing usage error contract
    with pytest.raises(RdeConfigError) as exc_info:
        build_run_request(
            flow=_flow,
            custom_dataset_function=_callback,
            config=None,
        )

    error = exc_info.value
    error_def = ERROR_CATALOG[1001]
    assert error.code == 1001
    assert error.name == error_def.name
    assert error_def.message_template in str(error)
    assert error_def.remediation in str(error)


def test_request_retains_config_root_and_validate_only__tc_ep_g2_104(
    tmp_path: Path,
) -> None:
    """TC-EP-G2-104: Normalization retains boundary inputs without conversion."""
    # Given: an opaque config source, explicit root, and validation-only mode
    config_source = object()

    # When: building the request with every boundary option
    request = build_run_request(
        flow=_flow,
        custom_dataset_function=None,
        config=config_source,
        root=tmp_path,
        validate_only=True,
    )

    # Then: all boundary values are retained verbatim
    assert request.root is tmp_path
    assert request.config_source is config_source
    assert request.validate_only is True


@pytest.mark.parametrize(
    "instance,field_name,new_value",
    [
        pytest.param(FlowTarget(_flow), "function", _callback, id="flow-target"),
        pytest.param(LegacyCallbackTarget(_callback), "function", _flow, id="legacy-target"),
        pytest.param(
            RunRequest(Path("."), FlowTarget(_flow)),
            "validate_only",
            True,
            id="run-request",
        ),
    ],
)
def test_request_dataclasses_are_frozen__tc_ep_g2_105(
    instance: Any,
    field_name: str,
    new_value: object,
) -> None:
    """TC-EP-G2-105: Every request dataclass rejects field mutation."""
    # Given: an instance of a public request dataclass
    # When / Then: mutating a declared field is forbidden
    with pytest.raises(FrozenInstanceError):
        setattr(instance, field_name, new_value)


@pytest.mark.parametrize(
    "instance",
    [
        pytest.param(FlowTarget(_flow), id="flow-target"),
        pytest.param(LegacyCallbackTarget(_callback), id="legacy-target"),
        pytest.param(RunRequest(Path("."), FlowTarget(_flow)), id="run-request"),
    ],
)
def test_request_dataclasses_use_slots__tc_ep_g2_106(instance: Any) -> None:
    """TC-EP-G2-106: Every request dataclass rejects undeclared attributes."""
    # Given: an instance of a slotted public request dataclass
    # When / Then: adding an undeclared attribute is forbidden
    with pytest.raises(TypeError):
        setattr(instance, "unexpected", True)


def test_neither_entry_point_preserves_v1_compatibility__tc_bv_g2_101() -> None:
    """TC-BV-G2-101: No entry point produces the callback-free legacy target."""
    # Given: neither public API entry point
    # When: normalizing the boundary request
    request = build_run_request(flow=None, custom_dataset_function=None, config=None)

    # Then: v1 callback-free run compatibility is represented explicitly
    assert isinstance(request.target, LegacyCallbackTarget)
    assert request.target.function is None


def test_omitted_root_captures_current_directory__tc_bv_g2_102(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-BV-G2-102: An omitted request root resolves to the current directory."""
    # Given: a known current working directory
    monkeypatch.chdir(tmp_path)

    # When: normalizing without an explicit root
    request = build_run_request(flow=_flow, custom_dataset_function=None, config=None)

    # Then: the request captures that directory as an absolute path
    assert request.root == tmp_path

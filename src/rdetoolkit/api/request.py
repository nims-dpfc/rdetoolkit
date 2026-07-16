"""Normalized requests shared by future execution entry points."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rdetoolkit.errors import ERROR_CATALOG, RdeConfigError


@dataclass(frozen=True, slots=True)
class FlowTarget:
    """A v2 flow selected for execution.

    Attributes:
        function: Flow callable preserved from the public API boundary.
    """

    function: Callable[..., object]


@dataclass(frozen=True, slots=True)
class LegacyCallbackTarget:
    """A v1-compatible dataset callback selected for execution.

    Attributes:
        function: Dataset callback, or ``None`` for callback-free v1 runs.
    """

    function: Callable[..., object] | None


ExecutionTarget = FlowTarget | LegacyCallbackTarget


@dataclass(frozen=True, slots=True)
class RunRequest:
    """Normalized execution request consumed by the unified Runner.

    Attributes:
        root: Root directory of the run.
        target: Flow or legacy callback execution target.
        config_source: Opaque configuration source for boundary normalization.
        validate_only: Whether execution stops after validation.
    """

    root: Path
    target: ExecutionTarget
    config_source: object | None = None
    validate_only: bool = False


def build_run_request(
    *,
    flow: Callable[..., object] | None,
    custom_dataset_function: Callable[..., object] | None,
    config: object | None,
    root: Path | None = None,
    validate_only: bool = False,
) -> RunRequest:
    """Normalize public execution arguments into one request contract.

    Args:
        flow: v2 flow callable, if selected.
        custom_dataset_function: v1 dataset callback, if selected.
        config: Configuration source retained for later normalization.
        root: Run root. Defaults to the current working directory.
        validate_only: Whether the future Runner should only validate inputs.

    Returns:
        A normalized, immutable run request.

    Raises:
        RdeConfigError: If both public entry points are supplied.
    """
    if flow is not None and custom_dataset_function is not None:
        error_def = ERROR_CATALOG[1001]
        message = f"{error_def.message_template} Remediation: {error_def.remediation}"
        error_cls: Any = RdeConfigError
        raise error_cls(
            code=1001,
            name=error_def.name,
            message=message,
        )

    target: ExecutionTarget = (
        FlowTarget(function=flow)
        if flow is not None
        else LegacyCallbackTarget(function=custom_dataset_function)
    )

    return RunRequest(
        root=Path.cwd() if root is None else root,
        target=target,
        config_source=config,
        validate_only=validate_only,
    )

"""Execution target adapters for the v2 Runner."""

from __future__ import annotations

from typing import Protocol

from rdetoolkit.api.request import ExecutionTarget, FlowTarget
from rdetoolkit.core.context import RunContext
from rdetoolkit.report.events import EventSink
from rdetoolkit.runner.execute import ExecutionResult, run_tile
from rdetoolkit.types import RdeConfig


class TargetInvoker(Protocol):
    """Adapter contract for invoking one normalized execution target."""

    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult:
        """Invoke a normalized target for one tile."""
        ...


class FlowInvoker:
    """Invoke a flow target through the existing eager ``run_tile`` core."""

    def invoke(
        self,
        target: ExecutionTarget,
        context: RunContext,
        *,
        event_sink: EventSink,
        run_id: str,
        config: RdeConfig,
    ) -> ExecutionResult:
        """Execute one flow tile without duplicating DI or call-log behavior.

        Args:
            target: Normalized flow target.
            context: Reserved values for the current tile.
            event_sink: Sink receiving node events.
            run_id: Active run identifier.
            config: Effective run configuration.

        Returns:
            Primary execution result returned by ``run_tile``.

        Raises:
            TypeError: If the target is not a Phase H flow target.
        """
        if not isinstance(target, FlowTarget):
            msg = "LegacyCallbackTarget execution is implemented in Phase J"
            raise TypeError(msg)
        return run_tile(
            target.function,
            context,
            event_sink=event_sink,
            run_id=run_id,
            config=config,
            emit_iteration_events=False,
        )

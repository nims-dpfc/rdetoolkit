"""Versioned v2 event schema and sinks."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, TextIO, runtime_checkable


def _require_nonempty(value: str, name: str) -> str:
    """Validate that a required event field is a non-empty string."""
    if not value:
        msg = f"Event field {name!r} must be a non-empty string (Design §8.1)"
        raise ValueError(msg)
    return value


@dataclass(frozen=True, slots=True)
class Event:
    """Observable event emitted during a v2 run.

    Attributes:
        run_id: Run identifier shared by all events in a run.
        name: Dot-separated event name.
        timestamp: Unix timestamp in seconds.
        node_id: Optional node id for node-scoped events.
        payload: Event-specific JSON-serializable payload.
        schema_version: Event schema version.
    """

    run_id: str
    name: str
    timestamp: float = field(default_factory=time.time)
    node_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1"

    @classmethod
    def run_started(cls, *, run_id: str) -> Event:
        """Create a run.started event.

        Args:
            run_id: Run identifier.

        Returns:
            Event named ``run.started``.
        """
        _require_nonempty(run_id, "run_id")
        return cls(run_id=run_id, name="run.started")

    @classmethod
    def run_completed(cls, *, run_id: str, status: str | None = None) -> Event:
        """Create a run.completed event.

        Args:
            run_id: Run identifier.
            status: Optional final run status.

        Returns:
            Event named ``run.completed``.
        """
        _require_nonempty(run_id, "run_id")
        payload = {} if status is None else {"status": status}
        return cls(run_id=run_id, name="run.completed", payload=payload)

    @classmethod
    def iteration_started(cls, *, run_id: str, index: int) -> Event:
        """Create an iteration.started event.

        Args:
            run_id: Run identifier.
            index: Zero-based iteration index.

        Returns:
            Event named ``iteration.started``.
        """
        _require_nonempty(run_id, "run_id")
        return cls(
            run_id=run_id,
            name="iteration.started",
            payload={"iteration_index": index},
        )

    @classmethod
    def iteration_completed(cls, *, run_id: str, index: int) -> Event:
        """Create an iteration.completed event.

        Args:
            run_id: Run identifier.
            index: Zero-based iteration index.

        Returns:
            Event named ``iteration.completed``.
        """
        _require_nonempty(run_id, "run_id")
        return cls(
            run_id=run_id,
            name="iteration.completed",
            payload={"iteration_index": index},
        )

    @classmethod
    def node_started(cls, *, run_id: str, node_id: str, call_id: str) -> Event:
        """Create a node.started event.

        Args:
            run_id: Run identifier (required, non-empty).
            node_id: Node identifier (required, non-empty).
            call_id: Runtime call identifier (required, non-empty).

        Returns:
            Event named ``node.started``.
        """
        _require_nonempty(run_id, "run_id")
        _require_nonempty(node_id, "node_id")
        _require_nonempty(call_id, "call_id")
        return cls(
            run_id=run_id,
            name="node.started",
            node_id=node_id,
            payload={"call_id": call_id},
        )

    @classmethod
    def node_completed(
        cls,
        *,
        run_id: str,
        node_id: str,
        call_id: str,
        duration_ms: float = 0.0,
    ) -> Event:
        """Create a node.completed event.

        Args:
            run_id: Run identifier (required, non-empty).
            node_id: Node identifier (required, non-empty).
            call_id: Runtime call identifier (required, non-empty).
            duration_ms: Execution duration in milliseconds.

        Returns:
            Event named ``node.completed``.
        """
        _require_nonempty(run_id, "run_id")
        _require_nonempty(node_id, "node_id")
        _require_nonempty(call_id, "call_id")
        return cls(
            run_id=run_id,
            name="node.completed",
            node_id=node_id,
            payload={"call_id": call_id, "duration_ms": duration_ms},
        )


    @classmethod
    def node_failed(
        cls,
        *,
        run_id: str,
        node_id: str,
        call_id: str,
        error: Exception | None = None,
        error_type: str = "",
        error_msg: str = "",
    ) -> Event:
        """Create a node.failed event.

        Args:
            run_id: Run identifier (required, non-empty).
            node_id: Node identifier (required, non-empty).
            call_id: Runtime call identifier (required, non-empty).
            error: Optional exception; overrides ``error_type``/``error_msg``.
            error_type: Exception class name.
            error_msg: Exception message.

        Returns:
            Event named ``node.failed``.
        """
        _require_nonempty(run_id, "run_id")
        _require_nonempty(node_id, "node_id")
        _require_nonempty(call_id, "call_id")
        if error is not None:
            error_type = type(error).__name__
            error_msg = str(error)
        return cls(
            run_id=run_id,
            name="node.failed",
            node_id=node_id,
            payload={
                "call_id": call_id,
                "error_type": error_type,
                "error_msg": error_msg,
            },
        )


    @classmethod
    def warning(cls, *, run_id: str, code: int, message: str) -> Event:
        """Create a warning event.

        Args:
            run_id: Run identifier.
            code: Warning code.
            message: Warning message.

        Returns:
            Event named ``warning``.
        """
        _require_nonempty(run_id, "run_id")
        return cls(
            run_id=run_id,
            name="warning",
            payload={"code": code, "message": message},
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event to a plain dict.

        Returns:
            Dict with ``schema_version`` as the first key.
        """
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "name": self.name,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "payload": self.payload,
        }

    @property
    def kind(self) -> str:
        """Legacy event kind name derived from the canonical dot name."""
        return self.name.replace(".", "_").replace("completed", "finished")


@runtime_checkable
class EventSink(Protocol):
    """Protocol for sinks that receive v2 events."""

    def open(self, run_id: str) -> None:
        """Open the sink for a run.

        Args:
            run_id: Run identifier.
        """
        ...

    def emit(self, event: Event) -> None:
        """Emit an event.

        Args:
            event: Event to emit.
        """
        ...

    def close(self) -> None:
        """Close the sink."""
        ...


class MemoryEventSink:
    """In-memory event sink for tests and inspection."""

    def __init__(self) -> None:
        self.run_id: str | None = None
        self.events: list[Event] = []
        self.closed = False

    def open(self, run_id: str) -> None:
        """Open the sink for a run.

        Args:
            run_id: Run identifier.
        """
        self.run_id = run_id
        self.closed = False

    def emit(self, event: Event) -> None:
        """Store an event in memory.

        Args:
            event: Event to store.
        """
        self.events.append(event)

    def close(self) -> None:
        """Close the sink."""
        self.closed = True


class FileEventSink:
    """JSONL event sink writing ``events_{run_id}.jsonl`` under a logs directory.

    Args:
        logs_dir: Directory that will contain per-run event logs.
    """

    def __init__(self, logs_dir: Path) -> None:
        self._logs_dir = logs_dir
        self._run_id: str | None = None
        self._file: TextIO | None = None

    def open(self, run_id: str) -> None:
        """Open the per-run event log and write the run metadata header.

        Args:
            run_id: Run identifier.
        """
        self._logs_dir.mkdir(parents=True, exist_ok=True)
        self._run_id = run_id
        path = self._logs_dir / f"events_{run_id}.jsonl"
        self._file = path.open("w", encoding="utf-8")
        header = {
            "schema_version": "1",
            "type": "run.meta",
            "run_id": run_id,
            "timestamp": time.time(),
        }
        self._write_line(header)

    def emit(self, event: Event) -> None:
        """Append an event JSON line.

        Args:
            event: Event to write.
        """
        self._write_line(event.to_dict())

    def close(self) -> None:
        """Close the event log if it is open."""
        if self._file is not None:
            self._file.close()
            self._file = None

    def _write_line(self, data: dict[str, Any]) -> None:
        if self._file is None:
            msg = "FileEventSink.open(run_id) must be called before emit()."
            raise RuntimeError(msg)
        self._file.write(json.dumps(data, ensure_ascii=False) + "\n")
        self._file.flush()

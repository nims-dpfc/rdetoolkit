"""V2 type definitions for rdetoolkit.

This module defines the core data types used across the v2 DAG-based workflow engine.

Note:
    This file is append-only. Do not modify existing v1 definitions.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True, slots=True)
class InputPaths:
    """Immutable input directory paths for v2 workflow processing.

    Mirrors the v1 RdeInputDirPaths structure with a simplified interface.

    Attributes:
        inputdata: Path to the input data directory.
        invoice: Path to the invoice directory.
        tasksupport: Path to the task support directory.
        raw: Optional raw input directory for tile-oriented modes.
    """

    inputdata: Path
    invoice: Path
    tasksupport: Path
    raw: Path | None = None


_FACTORY_TOKEN: object = object()


def _require_simple_filename(filename: str) -> None:
    """Reject path traversal in artifact filenames (must be a bare basename)."""
    from pathlib import PurePosixPath, PureWindowsPath  # noqa: PLC0415

    if (
        not filename
        or filename in {".", ".."}
        or PurePosixPath(filename).name != filename
        or PureWindowsPath(filename).name != filename
    ):
        msg = f"filename must be a simple basename without path components: {filename!r}"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class OutputContext:
    """Immutable output path context with method-based API for saving artifacts.

    Provides both directory paths and convenience methods for writing
    processed data to the correct output locations.

    v1 ``RdeOutputResourcePath`` field coverage:
        ``raw`` -> ``raw`` included.
        ``nonshared_raw`` -> ``nonshared_raw`` included.
        ``rawfiles`` excluded because it is an input file reference concept
        handled by ``InputPaths`` or ``IterationInfo``.
        ``struct`` -> ``struct`` included.
        ``main_image`` -> ``main_image`` included.
        ``other_image`` -> ``other_image`` included.
        ``meta`` -> ``meta`` included.
        ``thumbnail`` -> ``thumbnail`` included.
        ``logs`` -> ``logs`` included.
        ``invoice`` -> ``invoice`` included.
        ``invoice_schema_json`` and ``invoice_org`` are covered under the
        ``invoice`` directory.
        ``smarttable_rowfile`` excluded as a SmartTable runtime artifact for
        Phase D Runner or ``IterationInfo``.
        ``temp`` excluded because Design §4.2 omits it; use ``tempfile``.
        ``invoice_patch`` excluded as an advanced invoice patch feature outside
        ``OutputContext``.
        ``attachment`` -> ``attachment`` included.

    Attributes:
        struct: Path to the structured data directory.
        meta: Path to the metadata directory.
        main_image: Path to the main image directory.
        other_image: Path to the other image directory.
        thumbnail: Path to the thumbnail directory.
        attachment: Path to the attachment directory.
        nonshared_raw: Path to the non-shared raw data directory.
        raw: Path to the raw data directory.
        invoice: Path to the invoice directory.
        logs: Path to the logs directory.
    """

    struct: Path
    meta: Path
    main_image: Path
    other_image: Path
    thumbnail: Path
    raw: Path
    logs: Path
    attachment: Path
    nonshared_raw: Path
    invoice: Path
    _token: InitVar[object | None] = None

    def __post_init__(self, _token: object | None) -> None:
        if _token is not _FACTORY_TOKEN:
            msg = (
                "OutputContext cannot be constructed directly; use "
                "OutputContext.from_resource_paths() (Design §4.2: factory-only)"
            )
            raise TypeError(msg)

    @classmethod
    def from_resource_paths(cls, resource_paths: Any) -> OutputContext:
        """Create an output context from v1 resource paths.

        Directory creation is owned by the Runner. This factory only adapts the
        path bundle into the canonical v2 output context.

        Args:
            resource_paths: Object exposing v1 ``RdeOutputResourcePath`` fields.

        Returns:
            Canonical v2 output context.
        """
        return cls(
            struct=resource_paths.struct,
            meta=resource_paths.meta,
            main_image=resource_paths.main_image,
            other_image=resource_paths.other_image,
            thumbnail=resource_paths.thumbnail,
            attachment=resource_paths.attachment,
            nonshared_raw=resource_paths.nonshared_raw,
            raw=resource_paths.raw,
            invoice=resource_paths.invoice,
            logs=resource_paths.logs,
            _token=_FACTORY_TOKEN,
        )

    def save_csv(self, df: Any, filename: str) -> Path:
        """Save a DataFrame as CSV to the structured data directory.

        Args:
            df: A pandas-like DataFrame with a ``to_csv`` method.
            filename: Target filename (e.g. ``"normalized.csv"``).

        Returns:
            Path to the written CSV file.
        """
        _require_simple_filename(filename)
        self.struct.mkdir(parents=True, exist_ok=True)
        dest = self.struct / filename
        df.to_csv(dest, index=False)
        return dest

    def save_meta(self, metadata: Any) -> None:
        """Save metadata as JSON to the metadata directory.

        Args:
            metadata: A ``Metadata`` instance (with a ``.custom`` dict attribute)
                or a plain dict.
        """
        self.meta.mkdir(parents=True, exist_ok=True)
        dest = self.meta / "metadata.json"
        data = metadata.custom if hasattr(metadata, "custom") else metadata
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_graph(self, fig: Any, filename: str) -> Path:
        """Save a figure/graph to the main image directory.

        Args:
            fig: A figure object with a ``savefig`` or ``write_image`` method.
            filename: Target filename (e.g. ``"plot.png"``).

        Returns:
            Path to the written file.
        """
        _require_simple_filename(filename)
        self.main_image.mkdir(parents=True, exist_ok=True)
        dest = self.main_image / filename
        if hasattr(fig, "write_image"):
            fig.write_image(str(dest))
        elif hasattr(fig, "savefig"):
            fig.savefig(str(dest))
        else:
            msg = f"Unsupported figure type: {type(fig)}"
            raise TypeError(msg)
        return dest

    def save_bytes(self, content: bytes, filename: str) -> Path:
        """Save raw bytes to the structured data directory.

        Args:
            content: Binary content to write.
            filename: Target filename.

        Returns:
            Path to the written file.
        """
        _require_simple_filename(filename)
        self.struct.mkdir(parents=True, exist_ok=True)
        dest = self.struct / filename
        dest.write_bytes(content)
        return dest

    def save_thumbnail(self, image_path: Path) -> Path:
        """Copy an image to the thumbnail directory.

        Args:
            image_path: Source image file path.

        Returns:
            Path to the copied file in the thumbnail directory.
        """
        self.thumbnail.mkdir(parents=True, exist_ok=True)
        dest = self.thumbnail / image_path.name
        shutil.copy2(image_path, dest)
        return dest

    def save_main_image(self, image_path: Path) -> Path:
        """Copy an image to the main image directory.

        Args:
            image_path: Source image file path.

        Returns:
            Path to the copied file in the main image directory.
        """
        self.main_image.mkdir(parents=True, exist_ok=True)
        dest = self.main_image / image_path.name
        shutil.copy2(image_path, dest)
        return dest

    def copy_raw(self, source_path: Path) -> Path:
        """Copy a file to the raw data directory.

        Args:
            source_path: Source file path.

        Returns:
            Path to the copied file in the raw directory.
        """
        self.raw.mkdir(parents=True, exist_ok=True)
        dest = self.raw / source_path.name
        shutil.copy2(source_path, dest)
        return dest


@dataclass(slots=True)
class Metadata:
    """Mutable metadata container with custom and basic sections.

    Attributes:
        custom: User-defined metadata key-value pairs.
        basic: Optional basic/system metadata.
    """

    custom: dict[str, Any] = field(default_factory=dict)
    basic: dict[str, Any] | None = None

    def set(self, key: str, value: Any) -> None:
        """Set a custom metadata entry.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self.custom[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a custom metadata entry.

        Args:
            key: Metadata key.
            default: Value to return if key is not found.

        Returns:
            The value for the key, or *default*.
        """
        return self.custom.get(key, default)


@dataclass(frozen=True, slots=True)
class InvoiceData:
    """Container for parsed invoice data injected by the Runner.

    Attributes:
        raw: The raw invoice content dict.
        mode: Processing mode (e.g. ``"invoice"``, ``"excelinvoice"``).
        schema: Optional JSON schema for the invoice.
    """

    raw: dict[str, Any] = field(default_factory=dict)
    mode: str = ""
    schema: dict[str, Any] | None = None

    def get_field(self, key: str, default: Any = None) -> Any:
        """Get a top-level field from the raw invoice data.

        Args:
            key: Field name.
            default: Value to return if key is not found.

        Returns:
            The value for the key, or *default*.
        """
        return self.raw.get(key, default)

    def get_custom_fields(self) -> dict[str, Any]:
        """Extract custom (non-system) fields from the raw invoice data.

        Returns:
            Dict of fields whose keys do not start with ``"_"``.
        """
        return {k: v for k, v in self.raw.items() if not k.startswith("_")}


@dataclass(frozen=True, slots=True)
class IterationInfo:
    """Information about the current processing iteration.

    Attributes:
        index: Zero-based iteration index.
        total: Total number of iterations.
        mode: Processing mode name (e.g. 'invoice', 'excelinvoice').
    """

    index: int
    total: int
    mode: str


class V2SystemSettings(BaseModel):
    """Strict v2 system settings normalized by the Runner."""

    model_config = ConfigDict(extra="forbid")

    extended_mode: str = "invoice"


class V2ExecutionSettings(BaseModel):
    """Strict v2 execution settings."""

    model_config = ConfigDict(extra="forbid")

    type_check: str = "off"


class V2PolicySettings(BaseModel):
    """Strict v2 policy settings."""

    model_config = ConfigDict(extra="forbid")

    error_policy: str = "fail_fast"


class V2ProvenanceSettings(BaseModel):
    """Strict v2 provenance settings."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True


class RdeConfig(BaseModel):
    """Strict v2 Runner configuration.

    This model is separate from the v1 ``models.config.Config`` contract.
    """

    model_config = ConfigDict(extra="forbid")

    system: V2SystemSettings = Field(default_factory=V2SystemSettings)
    execution: V2ExecutionSettings = Field(default_factory=V2ExecutionSettings)
    policy: V2PolicySettings = Field(default_factory=V2PolicySettings)
    provenance: V2ProvenanceSettings = Field(default_factory=V2ProvenanceSettings)
    custom: dict[str, Any] = Field(default_factory=dict)


def _build_output_context(
    *,
    struct: Path,
    meta: Path,
    main_image: Path,
    other_image: Path,
    thumbnail: Path,
    raw: Path,
    logs: Path,
    attachment: Path,
    nonshared_raw: Path,
    invoice: Path,
) -> OutputContext:
    """Package-internal constructor for rdetoolkit-owned factories.

    User code must go through ``OutputContext.from_resource_paths()``.
    """
    return OutputContext(
        struct=struct,
        meta=meta,
        main_image=main_image,
        other_image=other_image,
        thumbnail=thumbnail,
        raw=raw,
        logs=logs,
        attachment=attachment,
        nonshared_raw=nonshared_raw,
        invoice=invoice,
        _token=_FACTORY_TOKEN,
    )


# --- Canonical v2 schema re-exports (Design §4.1.1) --------------------------
# ``rdetoolkit.types`` is the single canonical entry point for v2 schema types.
# NodeCallRecord and ValueRef join this list in Phase C (provenance).
from rdetoolkit.core.context import RunContext  # noqa: E402, F401
from rdetoolkit.report.events import Event, EventSink  # noqa: E402, F401
from rdetoolkit.report.run_report import RunReport  # noqa: E402, F401

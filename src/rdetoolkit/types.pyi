from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

@dataclass(frozen=True, slots=True)
class InputPaths:
    inputdata: Path
    invoice: Path
    tasksupport: Path
    raw: Path | None = ...

@dataclass(frozen=True, slots=True)
class OutputContext:
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
    @classmethod
    def from_resource_paths(cls, resource_paths: Any) -> OutputContext: ...
    def save_csv(self, df: Any, filename: str) -> Path: ...
    def save_meta(self, metadata: Any) -> None: ...
    def save_graph(self, fig: Any, filename: str) -> Path: ...
    def save_bytes(self, content: bytes, filename: str) -> Path: ...
    def save_thumbnail(self, image_path: Path) -> Path: ...
    def save_main_image(self, image_path: Path) -> Path: ...
    def copy_raw(self, source_path: Path) -> Path: ...

@dataclass(slots=True)
class Metadata:
    custom: dict[str, Any] = field(default_factory=dict)
    basic: dict[str, Any] | None = None
    def set(self, key: str, value: Any) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...

@dataclass(frozen=True, slots=True)
class InvoiceData:
    raw: dict[str, Any] = field(default_factory=dict)
    mode: str = ...
    schema: dict[str, Any] | None = None
    def get_field(self, key: str, default: Any = None) -> Any: ...
    def get_custom_fields(self) -> dict[str, Any]: ...

@dataclass(frozen=True, slots=True)
class IterationInfo:
    index: int
    total: int
    mode: str

class V2SystemSettings(BaseModel):
    model_config: ConfigDict
    extended_mode: str = ...

class V2ExecutionSettings(BaseModel):
    model_config: ConfigDict
    type_check: str = ...

class V2PolicySettings(BaseModel):
    model_config: ConfigDict
    error_policy: str = ...

class V2ProvenanceSettings(BaseModel):
    model_config: ConfigDict
    enabled: bool = ...

class RdeConfig(BaseModel):
    model_config: ConfigDict
    system: V2SystemSettings = Field(default_factory=V2SystemSettings)
    execution: V2ExecutionSettings = Field(default_factory=V2ExecutionSettings)
    policy: V2PolicySettings = Field(default_factory=V2PolicySettings)
    provenance: V2ProvenanceSettings = Field(default_factory=V2ProvenanceSettings)
    custom: dict[str, Any] = Field(default_factory=dict)

def _require_simple_filename(filename: str) -> None: ...
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
) -> OutputContext: ...

from rdetoolkit.core.context import RunContext as RunContext
from rdetoolkit.report.events import Event as Event
from rdetoolkit.report.events import EventSink as EventSink
from rdetoolkit.report.run_report import RunReport as RunReport

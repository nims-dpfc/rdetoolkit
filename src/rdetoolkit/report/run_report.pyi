from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class RunReport:
    run_id: str
    status: str
    flow_id: str
    mode: str
    started_at: str
    duration_ms: float
    config_digest: str
    iterations: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    error: dict[str, Any] | None = ...
    schema_version: str = ...
    def to_dict(self) -> dict[str, Any]: ...
    def to_json(self, *, indent: int | None = ...) -> str: ...
    @classmethod
    def from_json(cls, json_str: str) -> RunReport: ...

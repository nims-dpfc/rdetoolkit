from dataclasses import dataclass
from typing import Any, Protocol

class _Spec(Protocol):
    id: str

@dataclass(frozen=True, slots=True)
class FlowSpec:
    id: str
    name: str
    source_location: str

def register_node(spec: _Spec, wrapper: Any, fn: Any) -> None: ...
def get_node(node_id: str) -> _Spec: ...
def find_unstable_node_ids() -> tuple[str, ...]: ...
def register_flow(spec: FlowSpec, fn: Any) -> None: ...
def get_flow(flow_id: str) -> FlowSpec: ...

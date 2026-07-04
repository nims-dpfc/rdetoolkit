"""V2 RunContext and DI resolution algorithm.

RunContext holds Runner reserved types (InputPaths, OutputContext, etc.)
that can be injected at the flow boundary.

DI Resolution Priority:
    1. DAG edge result (upstream @node output, match by param_name)
    2. Runner reserved type (match by param_name AND param_type)
    3. UnconnectedInputError
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rdetoolkit.errors import UnconnectedInputError

if TYPE_CHECKING:
    from rdetoolkit.core.dag import DAG
    from rdetoolkit.core.node import NodeSpec
    from rdetoolkit.types import InputPaths, InvoiceData, IterationInfo, OutputContext, RdeConfig


def _build_reserved() -> dict[str, type]:
    """Build the reserved name-to-type mapping (lazy to avoid circular imports)."""
    from rdetoolkit.types import (  # noqa: PLC0415
        InputPaths,
        InvoiceData,
        IterationInfo,
        OutputContext,
        RdeConfig,
    )

    return {
        "paths": InputPaths,
        "out": OutputContext,
        "config": RdeConfig,
        "invoice": InvoiceData,
        "iteration": IterationInfo,
    }


# Populated on first access via _get_reserved().
_RESERVED: dict[str, type] | None = None


def _get_reserved() -> dict[str, type]:
    global _RESERVED  # noqa: PLW0603
    if _RESERVED is None:
        _RESERVED = _build_reserved()
    return _RESERVED


def get_reserved_mapping() -> dict[str, type]:
    """Return the reserved param-name → type mapping.

    This is the public API for accessing the RESERVED constant.
    """
    return _get_reserved()


# Module-level RESERVED for direct import.
# We use __getattr__ so the lazy import works at module level.
def __getattr__(name: str) -> Any:
    if name == "RESERVED":
        return _get_reserved()
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


class RunContext:
    """Runtime context providing Runner reserved types for DI resolution.

    Attributes:
        paths: Input directory paths (if available).
        out: Output directory context (if available).
        config: Strict v2 config (if available).
        invoice: Parsed invoice data (if available).
        iteration: Current iteration info (if available).
    """

    __slots__ = ("config", "invoice", "iteration", "out", "paths")

    def __init__(
        self,
        *,
        paths: InputPaths | None = None,
        out: OutputContext | None = None,
        config: RdeConfig | None = None,
        input_paths: InputPaths | None = None,
        output_context: OutputContext | None = None,
        invoice: InvoiceData | None = None,
        iteration: IterationInfo | None = None,
    ) -> None:
        self.paths = paths if paths is not None else input_paths
        self.out = out if out is not None else output_context
        self.config = config
        self.invoice = invoice
        self.iteration = iteration

    @property
    def input_paths(self) -> InputPaths | None:
        """Backward-compatible alias for the canonical ``paths`` slot."""
        return self.paths

    @property
    def output_context(self) -> OutputContext | None:
        """Backward-compatible alias for the canonical ``out`` slot."""
        return self.out

    def reserved_values(self) -> dict[str, Any]:
        """Return a mapping of reserved param-name -> value.

        Returns:
            Dict with reserved parameter names as keys and their instances as
            values. ``None``-valued entries are excluded.
        """
        mapping: dict[str, Any] = {}
        if self.paths is not None:
            mapping["paths"] = self.paths
        if self.out is not None:
            mapping["out"] = self.out
        if self.config is not None:
            mapping["config"] = self.config
        if self.invoice is not None:
            mapping["invoice"] = self.invoice
        if self.iteration is not None:
            mapping["iteration"] = self.iteration
        return mapping


def _find_edge_result(
    param_name: str,
    node_id: str,
    dag: DAG,
    results: dict[str, dict[str, Any]],
) -> tuple[bool, Any]:
    """Look up the edge result for a given input parameter.

    Searches DAG edges targeting this node for a matching to_port.
    Returns (True, value) if found, (False, None) otherwise.
    """
    edges = dag.edge_list()
    for from_id, to_id, from_port, to_port in edges:
        if to_id == node_id and to_port == param_name:
            node_results = results.get(from_id)
            if node_results is not None and from_port in node_results:
                return True, node_results[from_port]
    return False, None


def resolve_inputs(
    node_spec: NodeSpec,
    dag: DAG,
    results: dict[str, dict[str, Any]],
    context: RunContext,
) -> dict[str, Any]:
    """Resolve all input parameters for a node using the DI priority chain.

    Priority:
        1. DAG edge result (upstream @node output, match by param_name)
        2. Runner reserved type (match by param_name AND param_type)
        3. UnconnectedInputError

    Args:
        node_spec: The NodeSpec describing the node's input requirements.
        dag: The DAG containing edge information.
        results: Mapping of node_id -> {port_name: value} for completed nodes.
        context: RunContext providing reserved types.

    Returns:
        Dict mapping parameter names to resolved values.

    Raises:
        UnconnectedInputError: If a parameter cannot be resolved by name+type.
    """
    resolved: dict[str, Any] = {}
    reserved_map = _get_reserved()
    reserved_vals = context.reserved_values()

    for param_name, param_type in node_spec.input_schema.items():
        # Priority 1: DAG edge result (match by param_name)
        found, value = _find_edge_result(param_name, node_spec.id, dag, results)
        if found:
            resolved[param_name] = value
            continue

        # Priority 2: Runner reserved type (param_name AND param_type must both match)
        if (
            param_name in reserved_map
            and reserved_map[param_name] is param_type
            and param_name in reserved_vals
        ):
            resolved[param_name] = reserved_vals[param_name]
            continue

        # Priority 3: Unresolvable
        raise UnconnectedInputError(node_spec.id, param_name, param_type)

    return resolved

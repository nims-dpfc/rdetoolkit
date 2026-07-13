"""Commands for inspecting and linting registered v2 nodes."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict
from typing import Annotated, cast

import typer

from rdetoolkit.cli._v2_common import load_modules
from rdetoolkit.core import registry
from rdetoolkit.core.injection import find_duplicate_reserved_annotations
from rdetoolkit.core.node import NodeSpec
from rdetoolkit.errors import ERROR_CATALOG

app = typer.Typer(help="Inspect and lint registered v2 nodes.")


def find_duplicate_node_ids(specs: Sequence[NodeSpec]) -> Sequence[str]:
    """Return node ids that occur more than once."""
    counts = Counter(spec.id for spec in specs)
    return tuple(node_id for node_id, count in counts.items() if count > 1)


def _emit_usage_error(message: str) -> None:
    typer.echo(message, err=True)
    raise typer.Exit(code=3)


@app.command("list")
def list_nodes(
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
    modules: Annotated[
        list[str] | None,
        typer.Option("--module", help="Import a project module before listing; repeatable."),
    ] = None,
) -> None:
    """List nodes in the current process registry."""
    load_modules(modules or [])
    specs = cast(tuple[NodeSpec, ...], registry.list_nodes())
    values = [asdict(spec) for spec in specs]
    if as_json:
        typer.echo(json.dumps(values, sort_keys=True))
        return
    for value in values:
        typer.echo(value["id"])


@app.command()
def describe(
    node_id: Annotated[str, typer.Argument(metavar="<id>")],
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
    modules: Annotated[
        list[str] | None,
        typer.Option("--module", help="Import a project module before describing; repeatable."),
    ] = None,
) -> None:
    """Describe a registered node."""
    load_modules(modules or [])
    try:
        value = asdict(cast(NodeSpec, registry.get_node(node_id)))
    except KeyError:
        _emit_usage_error(f"Unknown node id: {node_id}")
    if as_json:
        typer.echo(json.dumps(value, sort_keys=True))
        return
    for name, field_value in value.items():
        typer.echo(f"{name}: {field_value}")


def _lint_messages() -> list[str]:
    nodes = cast(tuple[NodeSpec, ...], registry.list_nodes())
    messages = [
        f"E2001 duplicate node id {node_id}. {ERROR_CATALOG[2001].remediation}"
        for node_id in find_duplicate_node_ids(nodes)
    ]
    for spec in nodes:
        for parameter, schema in spec.input_schema.items():
            if schema["type_name"] == "typing.Any":
                messages.append(f"Missing type annotation: {spec.id}.{parameter}")
    messages.extend(
        f"E2005 unstable node id {node_id}. {ERROR_CATALOG[2005].remediation}"
        for node_id in registry.find_unstable_node_ids()
    )
    for flow_spec in registry.list_flows():
        duplicates = find_duplicate_reserved_annotations(registry.get_flow_function(flow_spec.id))
        for reserved_type, parameter_names in duplicates.items():
            type_name = getattr(reserved_type, "__name__", str(reserved_type))
            messages.append(
                f"E2006 duplicate reserved annotation {type_name} on "
                f"{flow_spec.id}: {', '.join(parameter_names)}. {ERROR_CATALOG[2006].remediation}",
            )
    return messages


@app.command()
def lint(
    modules: Annotated[
        list[str] | None,
        typer.Option("--module", help="Import a project module before linting; repeatable."),
    ] = None,
) -> None:
    """Run static checks over the current node and flow registries."""
    load_modules(modules or [])
    messages = _lint_messages()
    if not messages:
        typer.echo("0 violations")
        return
    for message in messages:
        typer.echo(message)
    raise typer.Exit(code=3)

"""Commands for discovering templates and generating concrete skeletons."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from rdetoolkit.cli._v2_common import load_modules
from rdetoolkit.templates import registry
from rdetoolkit.templates.registry import TemplateMethodSpec, TemplateSpec

app = typer.Typer(help="Inspect registered ProcessingTemplate skeletons.")


def _emit_usage_error(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(code=3)


def _find_template(name: str) -> TemplateSpec:
    try:
        return registry.get_template(name)
    except KeyError:
        _emit_usage_error(f"Unknown processing template: {name}")


@app.command("list")
def list_templates(
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
    modules: Annotated[
        list[str] | None,
        typer.Option("--module", help="Import a project module before listing; repeatable."),
    ] = None,
) -> None:
    """List registered depth-1 template skeletons."""
    load_modules(modules or [])
    from rdetoolkit.plugin import discover_plugins  # noqa: PLC0415

    discover_plugins()
    values = [asdict(spec) for spec in registry.list_templates()]
    if as_json:
        typer.echo(json.dumps(values, sort_keys=True))
        return
    for value in values:
        typer.echo(value["id"])


@app.command()
def describe(
    template_id: Annotated[str, typer.Argument(metavar="<name>")],
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
    modules: Annotated[
        list[str] | None,
        typer.Option("--module", help="Import a project module before describing; repeatable."),
    ] = None,
) -> None:
    """Describe a registered template skeleton."""
    load_modules(modules or [])
    value = asdict(_find_template(template_id))
    if as_json:
        typer.echo(json.dumps(value, sort_keys=True))
        return
    for name, field_value in value.items():
        typer.echo(f"{name}: {field_value}")


def _identifier(value: str) -> str:
    words = [part for part in re.split(r"[^A-Za-z0-9]+", value) if part]
    candidate = "".join(word[:1].upper() + word[1:] for word in words)
    return candidate or "GeneratedProcessing"


def _annotation(type_name: str) -> str:
    return type_name.rsplit(".", maxsplit=1)[-1]


def _render_slot(method: TemplateMethodSpec) -> str:
    parameters = ", ".join(
        f"{parameter.name}: {_annotation(parameter.type_name)}"
        for parameter in method.parameters
    )
    separator = ", " if parameters else ""
    return_type = _annotation(method.return_type)
    return (
        f"    def {method.name}(self{separator}{parameters}) -> {return_type}:\n"
        f"        # TODO: implement the {method.name} template slot.\n"
        "        raise NotImplementedError\n"
    )


def _render_processing_module(spec: TemplateSpec) -> str:
    module_name, _, skeleton_name = spec.id.rpartition(".")
    class_name = _identifier(skeleton_name.removesuffix("Template") + "Processing")
    methods = "\n".join(_render_slot(method) for method in spec.slots)
    return (
        '"""Generated ProcessingTemplate implementation."""\n\n'
        "from __future__ import annotations\n\n"
        f"from {module_name} import {skeleton_name}\n\n\n"
        f"class {class_name}({skeleton_name}):\n"
        '    """TODO: implement each required domain slot."""\n\n'
        f"{methods}"
    )


def _render_sample_test(spec: TemplateSpec) -> str:
    skeleton_name = spec.name
    class_name = _identifier(skeleton_name.removesuffix("Template") + "Processing")
    first_slot = spec.slots[0].name if spec.slots else None
    assertion = (
        f"    # TODO: call processing.{first_slot}(rde_paths) and assert its result.\n"
        if first_slot is not None
        else "    # TODO: assert the generated processing behavior.\n"
    )
    return (
        '"""Sample tests for the generated processing template."""\n\n'
        "from processing import "
        f"{class_name}\n\n\n"
        "def test_generated_processing(rde_paths, rde_out, rde_config, rde_invoice) -> None:\n"
        f"    processing = {class_name}()\n"
        f"{assertion}"
        "    assert processing is not None\n"
    )


def generate_processing_template(name: str, modules: Sequence[str], output_dir: Path) -> None:
    """Generate a TODO implementation and sample test for a skeleton.

    Args:
        name: Full template id or unambiguous skeleton class name.
        modules: Dotted provider modules imported before registry lookup.
        output_dir: Directory receiving generated files.
    """
    load_modules(modules)
    spec = _find_template(name)
    output_dir.mkdir(parents=True, exist_ok=True)
    processing_path = output_dir / "processing.py"
    test_dir = output_dir / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_path = test_dir / "test_processing.py"
    processing_path.write_text(_render_processing_module(spec), encoding="utf-8")
    test_path.write_text(_render_sample_test(spec), encoding="utf-8")
    typer.echo(f"Generated {processing_path}")
    typer.echo(f"Generated {test_path}")

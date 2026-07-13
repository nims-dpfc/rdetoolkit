"""Report source locations that may need v2 migration.

Class findings use a best-effort structural heuristic because v1 defines no
common handler base class. Review those findings manually.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Never

import typer

app = typer.Typer(help="Inspect Python source for v1 migration points.")
_HANDLER_POSITIONAL_ARGUMENTS = 3


@dataclass(frozen=True, slots=True)
class Finding:
    """One source migration finding."""

    line: int
    category: str


def _usage_error(message: str) -> Never:
    typer.echo(message, err=True)
    raise typer.Exit(code=3)


@app.command()
def check(path: Annotated[Path, typer.Argument(metavar="[path]")] = Path(".")) -> None:
    """Scan one Python file or all Python files beneath a directory."""
    if not path.exists():
        _usage_error(f"Path does not exist: {path}")
    files = [path] if path.is_file() else sorted(path.rglob("*.py"))
    for source_path in files:
        _report_file(source_path)


def _report_file(path: Path) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        typer.echo(f"{path}:{getattr(exc, 'lineno', 0) or 0}: unparseable: {exc}")
        return
    for finding in _find_migration_points(tree):
        typer.echo(f"{path}:{finding.line}: {finding.category}")


def _find_migration_points(tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and any(keyword.arg == "custom_dataset_function" for keyword in node.keywords):
            findings.append(Finding(node.lineno, "custom_dataset_function keyword"))
        if isinstance(node, ast.Name) and node.id == "RdeOutputResourcePath":
            findings.append(Finding(node.lineno, "direct RdeOutputResourcePath reference"))
        if isinstance(node, ast.ClassDef) and _has_legacy_handler_shape(node):
            findings.append(Finding(node.lineno, f"possible old handler class {node.name}"))
    return findings


def _has_legacy_handler_shape(class_node: ast.ClassDef) -> bool:
    return any(
        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and _matches_handler_method(item)
        for item in class_node.body
    )


def _matches_handler_method(method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    positional = [*method.args.posonlyargs, *method.args.args]
    if len(positional) != _HANDLER_POSITIONAL_ARGUMENTS or positional[0].arg not in {"self", "cls"}:
        return False
    output_arg = positional[2]
    return output_arg.arg == "resource_paths" or _annotation_name(output_arg.annotation) == "RdeOutputResourcePath"


def _annotation_name(annotation: ast.expr | None) -> str | None:
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    return None

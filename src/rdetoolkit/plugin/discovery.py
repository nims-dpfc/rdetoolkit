"""Discover declarative rdetoolkit plugins from package entry points."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib import metadata
from typing import Any

from rdetoolkit.core import registry as node_registry
from rdetoolkit.templates import registry as template_registry


@dataclass(frozen=True, slots=True)
class FormatHandler:
    """Declarative description of one plugin-provided file format.

    Attributes:
        name: Human-readable format name.
        extensions: Supported filename extensions, including leading dots.
        target: Qualified ``pkg.mod:attr`` reference shown to users.
    """

    name: str
    extensions: tuple[str, ...]
    target: str


@dataclass(frozen=True, slots=True)
class DiscoveredPlugin:
    """Registry provenance and format declarations for one loaded plugin.

    Attributes:
        name: Entry-point name.
        node_ids: Node identifiers registered while loading the plugin.
        template_ids: Template identifiers registered while loading the plugin.
        format_handlers: Declarative format handlers supplied by the plugin.
    """

    name: str
    node_ids: tuple[str, ...]
    template_ids: tuple[str, ...]
    format_handlers: tuple[FormatHandler, ...]


_discovered: dict[tuple[str, str], DiscoveredPlugin] = {}


def _ids(specs: tuple[Any, ...]) -> tuple[str, ...]:
    return tuple(str(spec.id) for spec in specs)


def _handlers(provider: object) -> tuple[FormatHandler, ...]:
    handlers = getattr(provider, "FORMAT_HANDLERS", ())
    if not isinstance(handlers, tuple) or not all(isinstance(item, FormatHandler) for item in handlers):
        msg = "FORMAT_HANDLERS must be a tuple of rdetoolkit.plugin.FormatHandler values"
        raise TypeError(msg)
    return handlers


def _warning(plugin_name: str, exc: Exception) -> None:
    sys.stderr.write(
        f"Plugin {plugin_name!r} was skipped: {exc}. "
        "Remediation: reinstall or upgrade the plugin, then verify its rdetoolkit.plugins entry point.\n",
    )


def _load_plugin(entry_point: Any) -> DiscoveredPlugin:
    before_nodes = set(_ids(node_registry.list_nodes()))
    before_templates = set(_ids(template_registry.list_templates()))
    provider = entry_point.load()
    node_ids = tuple(node_id for node_id in _ids(node_registry.list_nodes()) if node_id not in before_nodes)
    template_ids = tuple(
        template_id
        for template_id in _ids(template_registry.list_templates())
        if template_id not in before_templates
    )
    return DiscoveredPlugin(
        name=str(entry_point.name),
        node_ids=node_ids,
        template_ids=template_ids,
        format_handlers=_handlers(provider),
    )


def discover_plugins() -> tuple[DiscoveredPlugin, ...]:
    """Load and describe installed ``rdetoolkit.plugins`` entry points.

    A failing or contract-incompatible third-party entry is reported to stderr
    and skipped so inspection commands remain usable.

    Returns:
        Successfully discovered plugins in entry-point order.
    """
    plugins: list[DiscoveredPlugin] = []
    for entry_point in metadata.entry_points(group="rdetoolkit.plugins"):
        key = (str(entry_point.name), str(entry_point.value))
        cached = _discovered.get(key)
        if cached is not None:
            plugins.append(cached)
            continue
        try:
            plugin = _load_plugin(entry_point)
        except Exception as exc:  # noqa: BLE001
            _warning(str(entry_point.name), exc)
            continue
        _discovered[key] = plugin
        plugins.append(plugin)
    return tuple(plugins)

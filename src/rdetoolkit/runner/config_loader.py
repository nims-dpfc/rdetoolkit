"""Configuration loading for the v2 Runner."""

from __future__ import annotations

import copy
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from rdetoolkit.types import RdeConfig


def load_config(
    root: Path,
    overrides: Mapping[str, Any] | None = None,
) -> RdeConfig:
    """Load strict v2 Runner configuration.

    The fallback chain is ``rdeconfig.yaml`` first, then
    ``pyproject.toml`` ``[tool.rdetoolkit]``, then ``RdeConfig()`` defaults.
    Explicit overrides win over file values.

    Args:
        root: Directory containing optional config files.
        overrides: Values merged over the loaded config.

    Returns:
        Effective v2 configuration.

    Raises:
        pydantic.ValidationError: If a file or override contains unknown or
            invalid keys for ``RdeConfig`` or its child models.
    """
    config_data = _load_config_data(root)
    if overrides:
        config_data = _deep_merge(config_data, dict(overrides))
    return RdeConfig(**config_data)


def _load_config_data(root: Path) -> dict[str, Any]:
    rdeconfig_path = root / "rdeconfig.yaml"
    if rdeconfig_path.exists():
        return _load_yaml_mapping(rdeconfig_path)

    pyproject_path = root / "pyproject.toml"
    if pyproject_path.exists():
        return _load_pyproject_mapping(pyproject_path)

    return {}


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw_data is None:
        return {}
    if not isinstance(raw_data, dict):
        msg = f"{path.name} must contain a mapping at the top level"
        raise TypeError(msg)
    return dict(raw_data)


def _load_pyproject_mapping(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    if not isinstance(tool, dict):
        return {}
    rdetoolkit_data = tool.get("rdetoolkit", {})
    if not isinstance(rdetoolkit_data, dict):
        return {}
    return dict(rdetoolkit_data)


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(base))
    for key, value in overlay.items():
        existing = result.get(key)
        if isinstance(existing, dict) and isinstance(value, Mapping):
            result[key] = _deep_merge(existing, value)
        else:
            result[key] = copy.deepcopy(value)
    return result

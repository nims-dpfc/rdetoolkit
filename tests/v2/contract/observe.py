"""Observation helper for v2 runs compared against frozen v1 snapshots.

``_generate.py`` owns the v1 oracle and stays byte-frozen, so this module
reuses its walkers instead of re-implementing them: the observed keys, the
``data/`` relative POSIX form, the sort order and the ``normalize_snapshot``
volatility rules are therefore identical on both sides of a parity assertion.

The single deliberate asymmetry is ``data/logs/`` (Design §6.3 addendum,
Session I6-1 ruling #2): v1 writes ``rdesys_<ts>.log`` there while v2 writes
its RunReport JSON, so the *contents* of that one directory are excluded from
tree parity. The directory entry itself is kept, and the exclusion is applied
to both sides through :func:`parity_view`, so a frozen expected file is never
edited to make a comparison pass.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from tests.v2.contract.fixtures import _generate

#: Directory whose contents are contractually excluded from tree parity.
LOGS_PREFIX = "data/logs/"

#: Observation keys produced by :func:`observe_v2_run`.
PARITY_KEYS = ("output_tree", "raw_sha256", "invoices")


def observe_v2_run(root: Path, *, exclude_logs: bool = True) -> dict[str, Any]:
    """Observe the output artifacts a v2 run left under ``root``.

    Args:
        root: Run root that owns the ``data`` directory (or the data root).
        exclude_logs: Drop entries below ``data/logs/`` from the output tree.

    Returns:
        Normalized ``output_tree`` / ``raw_sha256`` / ``invoices`` observation
        directly comparable with the same keys of a frozen v1 snapshot passed
        through :func:`parity_view`.
    """
    data_root = root if root.name == "data" else root / "data"
    observation = {
        "output_tree": _generate._output_tree(data_root),  # noqa: SLF001 -- frozen v1 walker is the contract
        "invoices": _generate._invoice_outputs(data_root),  # noqa: SLF001
        "raw_sha256": _generate._raw_hashes(data_root),  # noqa: SLF001
    }
    normalized: dict[str, Any] = _generate.normalize_snapshot(observation, roots=(root,))
    return _strip_logs(normalized) if exclude_logs else normalized


def parity_view(observed: Mapping[str, Any], *, exclude_logs: bool = True) -> dict[str, Any]:
    """Project a frozen v1 observation onto the comparable parity keys.

    Args:
        observed: The ``observed`` mapping of a frozen snapshot.
        exclude_logs: Drop entries below ``data/logs/`` from the output tree.

    Returns:
        A new mapping holding only :data:`PARITY_KEYS`, log-excluded in memory.
        The frozen file on disk is never modified.
    """
    view = {key: observed[key] for key in PARITY_KEYS}
    return _strip_logs(view) if exclude_logs else view


def _strip_logs(observation: dict[str, Any]) -> dict[str, Any]:
    """Remove entries *below* ``data/logs/`` while keeping the directory itself."""
    tree = observation["output_tree"]
    return {
        **observation,
        "output_tree": {
            "directories": [path for path in tree["directories"] if not _below_logs(path)],
            "files": [path for path in tree["files"] if not _below_logs(path)],
        },
    }


def _below_logs(path: str) -> bool:
    return path.startswith(LOGS_PREFIX) and path != LOGS_PREFIX

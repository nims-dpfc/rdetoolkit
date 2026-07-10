"""Tile iteration for the v2 Runner."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from rdetoolkit.domain.mode import selected_input_checker
from rdetoolkit.models.rde2types import RdeInputDirPaths
from rdetoolkit.runner.mode_resolver import ModeKind
from rdetoolkit.runner.paths import TileOutputPaths, resolve_tile_paths
from rdetoolkit.types import InputPaths, IterationInfo, OutputContext


class TileIterator(Protocol):
    """Callable shape for producing per-tile Runner reserved values."""

    def __call__(
        self,
        mode: ModeKind,
        inputdata_path: Path,
        unpacked_dir_path: Path,
        base_output_dir: Path,
    ) -> Iterator[tuple[IterationInfo, InputPaths, OutputContext]]:
        """Yield per-tile ``IterationInfo``, ``InputPaths``, and ``OutputContext`` triples."""
        ...


def iterate_tiles(
    mode: ModeKind,
    inputdata_path: Path,
    unpacked_dir_path: Path,
    base_output_dir: Path,
) -> Iterator[tuple[IterationInfo, InputPaths, OutputContext]]:
    """Yield v1-compatible tile contexts for all Runner modes.

    Args:
        mode: Effective Runner mode.
        inputdata_path: Directory containing input files.
        unpacked_dir_path: Directory used by legacy input checkers.
        base_output_dir: Root ``data`` output directory.

    Yields:
        Per-tile ``(IterationInfo, InputPaths, OutputContext)`` triples.
    """
    src_paths = RdeInputDirPaths(
        inputdata=inputdata_path,
        invoice=inputdata_path.parent / "invoice",
        tasksupport=inputdata_path.parent / "tasksupport",
    )
    checker = selected_input_checker(
        src_paths,
        unpacked_dir_path,
        _mode_for_checker(mode),
        config=None,
    )
    rawfiles_by_tile, _special = checker.parse(inputdata_path)
    total = len(rawfiles_by_tile)

    for idx, rawfiles in enumerate(rawfiles_by_tile):
        tile_paths = resolve_tile_paths(base_output_dir, idx)
        _create_output_dirs(tile_paths)
        rawfiles_tuple = tuple(rawfiles)
        yield (
            IterationInfo(index=idx, total=total, mode=mode.value),
            InputPaths(
                inputdata=inputdata_path,
                invoice=src_paths.invoice,
                tasksupport=src_paths.tasksupport,
                raw=rawfiles_tuple[0] if len(rawfiles_tuple) == 1 else None,
                rawfiles=rawfiles_tuple,
            ),
            OutputContext.from_resource_paths(tile_paths),
        )


def _mode_for_checker(mode: ModeKind) -> str | None:
    if mode is ModeKind.multidatatile:
        return "multidatatile"
    if mode is ModeKind.rdeformat:
        return "rdeformat"
    return None


def _create_output_dirs(tile_paths: TileOutputPaths) -> None:
    for path in (
        tile_paths.struct,
        tile_paths.meta,
        tile_paths.main_image,
        tile_paths.other_image,
        tile_paths.thumbnail,
        tile_paths.attachment,
        tile_paths.nonshared_raw,
        tile_paths.raw,
        tile_paths.invoice,
        tile_paths.logs,
    ):
        path.mkdir(parents=True, exist_ok=True)

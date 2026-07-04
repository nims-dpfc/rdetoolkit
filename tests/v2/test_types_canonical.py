"""Canonical acceptance tests for rdetoolkit v2 reserved types — Session A2.

Written before implementation (TDD Red phase).
Target: make all tests pass in the codex-worker Green phase.

TC-TYPES-001..015 as inventoried in local/develop/v2/tasks/session_a2.md.
Authority: local/develop/v2/Design.md §4.2 and decisions_pre_A1.md §A2.

Compat anchors (expected to PASS already in Red phase):
    TC-TYPES-014 — OutputContext.rawfiles absent (never existed)
    TC-TYPES-015 — OutputContext.temp absent (never existed)
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helper — builds a valid v1 RdeOutputResourcePath for factory tests.
# Defined here so each test class can call it without duplication.
# Uses a local import to avoid module-level failures.
# ---------------------------------------------------------------------------


def _make_v1_paths(base: Path):  # type: ignore[return]  # no annotation avoids circular import
    """Return a minimal valid RdeOutputResourcePath rooted at *base*."""
    from rdetoolkit.models.rde2types import RdeOutputResourcePath  # noqa: PLC0415

    return RdeOutputResourcePath(
        raw=base / "raw",
        nonshared_raw=base / "nonshared_raw",
        rawfiles=(),
        struct=base / "struct",
        main_image=base / "main_image",
        other_image=base / "other_image",
        meta=base / "meta",
        thumbnail=base / "thumbnail",
        logs=base / "logs",
        invoice=base / "invoice",
        invoice_schema_json=base / "invoice" / "invoice.schema.json",
        invoice_org=base / "invoice" / "invoice.json",
        attachment=base / "attachment",
    )


# ---------------------------------------------------------------------------
# TC-TYPES-001: OutputContext canonical field set
# ---------------------------------------------------------------------------


class TestOutputContextCanonicalFields:
    """OutputContext must have exactly the 10 directories defined in Design §4.2."""

    def test_output_context_has_exactly_ten_directories__tc_types_001(self) -> None:
        """TC-TYPES-001: Field names match the 10-dir canonical set from Design §4.2."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        expected = {
            "struct",
            "meta",
            "main_image",
            "other_image",
            "thumbnail",
            "attachment",
            "nonshared_raw",
            "raw",
            "invoice",
            "logs",
        }
        actual = {f.name for f in dataclasses.fields(OutputContext)}
        assert actual == expected, (
            f"OutputContext field mismatch.\n"
            f"  Expected : {sorted(expected)}\n"
            f"  Got      : {sorted(actual)}\n"
            f"  Missing  : {sorted(expected - actual)}\n"
            f"  Extra    : {sorted(actual - expected)}"
        )


# ---------------------------------------------------------------------------
# TC-TYPES-002: from_resource_paths() factory
# ---------------------------------------------------------------------------


class TestOutputContextFactory:
    """The canonical public construction path for OutputContext is from_resource_paths()."""

    def test_from_resource_paths_exists_and_returns_output_context__tc_types_002(
        self, tmp_path: Path
    ) -> None:
        """TC-TYPES-002: from_resource_paths(v1_paths) exists and returns OutputContext."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert hasattr(OutputContext, "from_resource_paths"), (
            "OutputContext.from_resource_paths() classmethod must exist. "
            "Direct __init__ construction is the non-public path."
        )
        v1_paths = _make_v1_paths(tmp_path)
        ctx = OutputContext.from_resource_paths(v1_paths)
        assert isinstance(ctx, OutputContext)
        assert ctx.struct == tmp_path / "struct"
        assert ctx.raw == tmp_path / "raw"
        assert ctx.logs == tmp_path / "logs"
        assert ctx.attachment == tmp_path / "attachment"
        assert ctx.nonshared_raw == tmp_path / "nonshared_raw"
        assert ctx.invoice == tmp_path / "invoice"


# ---------------------------------------------------------------------------
# TC-TYPES-003: save_bytes() — canonical name (renamed from save_file)
# ---------------------------------------------------------------------------


class TestOutputContextSaveBytes:
    """OutputContext.save_bytes() writes bytes; the old save_file() name is retired."""

    def test_save_bytes_method_exists_and_writes_binary__tc_types_003(
        self, tmp_path: Path
    ) -> None:
        """TC-TYPES-003: save_bytes(content, filename) writes bytes and returns the path."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert hasattr(OutputContext, "save_bytes"), (
            "OutputContext must have save_bytes(), not save_file(). "
            "Method was renamed for name-meaning alignment."
        )
        ctx = OutputContext.from_resource_paths(_make_v1_paths(tmp_path))
        result = ctx.save_bytes(b"canonical bytes", "output.bin")
        assert result.exists(), "save_bytes() must write the file to disk"
        assert result.read_bytes() == b"canonical bytes"


# ---------------------------------------------------------------------------
# TC-TYPES-004: copy_raw() — canonical name (renamed from save_raw)
# ---------------------------------------------------------------------------


class TestOutputContextCopyRaw:
    """OutputContext.copy_raw() copies a source file; save_raw() name is retired."""

    def test_copy_raw_method_exists_and_copies_file__tc_types_004(
        self, tmp_path: Path
    ) -> None:
        """TC-TYPES-004: copy_raw(source) copies source into the raw directory."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert hasattr(OutputContext, "copy_raw"), (
            "OutputContext must have copy_raw(), not save_raw(). "
            "Method was renamed for name-meaning alignment."
        )
        src = tmp_path / "source_data.raw"
        src.write_bytes(b"original raw content")
        ctx = OutputContext.from_resource_paths(_make_v1_paths(tmp_path))
        result = ctx.copy_raw(src)
        assert result.exists(), "copy_raw() must produce a file in the raw directory"
        assert result.read_bytes() == b"original raw content"
        assert result.name == src.name


# ---------------------------------------------------------------------------
# TC-TYPES-005/006: Old method names must not exist after the rename
# ---------------------------------------------------------------------------


class TestOutputContextDeprecatedMethodsAbsent:
    """save_file and save_raw must not appear on OutputContext after the rename."""

    def test_save_file_does_not_exist_on_output_context__tc_types_005(self) -> None:
        """TC-TYPES-005: save_file() must NOT exist (renamed to save_bytes())."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert not hasattr(OutputContext, "save_file"), (
            "save_file() must be removed from OutputContext. "
            "It was renamed to save_bytes() for name-meaning alignment."
        )

    def test_save_raw_does_not_exist_on_output_context__tc_types_006(self) -> None:
        """TC-TYPES-006: save_raw() must NOT exist (renamed to copy_raw())."""
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert not hasattr(OutputContext, "save_raw"), (
            "save_raw() must be removed from OutputContext. "
            "It was renamed to copy_raw() for name-meaning alignment."
        )


# ---------------------------------------------------------------------------
# TC-TYPES-007/008: InputPaths.raw — the 4th field (Path | None, default None)
# ---------------------------------------------------------------------------


class TestInputPathsRawField:
    """InputPaths must have a 4th field raw: Path | None with default None."""

    def test_input_paths_has_raw_field_defaulting_to_none__tc_types_007(self) -> None:
        """TC-TYPES-007: InputPaths.raw exists with None default; total field count is 4."""
        from rdetoolkit.types import InputPaths  # noqa: PLC0415

        field_names = {f.name for f in dataclasses.fields(InputPaths)}
        assert "raw" in field_names, (
            "InputPaths must have a raw: Path | None field per Design §4.2"
        )
        assert len(dataclasses.fields(InputPaths)) == 4, (
            f"InputPaths must have exactly 4 fields, got {len(dataclasses.fields(InputPaths))}: "
            f"{field_names}"
        )
        # Omitting raw must work (default None)
        paths = InputPaths(
            inputdata=Path("/data/inputdata"),
            invoice=Path("/data/invoice"),
            tasksupport=Path("/data/tasksupport"),
        )
        assert paths.raw is None

    def test_input_paths_raw_accepts_path_value__tc_types_008(self) -> None:
        """TC-TYPES-008: InputPaths.raw can be set to a Path (non-None)."""
        from rdetoolkit.types import InputPaths  # noqa: PLC0415

        raw_path = Path("/data/raw_tiles")
        paths = InputPaths(
            inputdata=Path("/data/inputdata"),
            invoice=Path("/data/invoice"),
            tasksupport=Path("/data/tasksupport"),
            raw=raw_path,
        )
        assert paths.raw == raw_path


# ---------------------------------------------------------------------------
# TC-TYPES-009..012: Reserved mapping — canonical 5-key dict
# ---------------------------------------------------------------------------


class TestReservedMapping:
    """get_reserved_mapping() must return the canonical 5-key mapping from Design §4.1."""

    def test_reserved_mapping_has_exactly_five_keys__tc_types_009(self) -> None:
        """TC-TYPES-009: Key set == {"paths","out","config","invoice","iteration"}."""
        from rdetoolkit.core.context import get_reserved_mapping  # noqa: PLC0415

        mapping = get_reserved_mapping()
        expected_keys = {"paths", "out", "config", "invoice", "iteration"}
        assert set(mapping.keys()) == expected_keys, (
            f"Reserved mapping key mismatch.\n"
            f"  Expected : {sorted(expected_keys)}\n"
            f"  Got      : {sorted(mapping.keys())}\n"
            f"  Missing  : {sorted(expected_keys - set(mapping.keys()))}\n"
            f"  Extra    : {sorted(set(mapping.keys()) - expected_keys)}"
        )

    def test_reserved_mapping_does_not_contain_deprecated_output_key__tc_types_010(
        self,
    ) -> None:
        """TC-TYPES-010: 'output' must not appear — replaced by 'out' per Design §4.1."""
        from rdetoolkit.core.context import get_reserved_mapping  # noqa: PLC0415

        mapping = get_reserved_mapping()
        assert "output" not in mapping, (
            "Key 'output' must be replaced by 'out' in the reserved mapping. "
            "The old name 'output' was the source of the B7 divergence."
        )

    def test_reserved_mapping_does_not_contain_context_key__tc_types_011(self) -> None:
        """TC-TYPES-011: 'context' must not appear — it is not one of the 5 reserved names."""
        from rdetoolkit.core.context import get_reserved_mapping  # noqa: PLC0415

        mapping = get_reserved_mapping()
        assert "context" not in mapping, (
            "Key 'context' (RunContext itself) must be removed from reserved mapping. "
            "RunContext is not a user-injectable parameter — only the 5 named types are."
        )

    def test_reserved_mapping_types_for_paths_out_config__tc_types_012(self) -> None:
        """TC-TYPES-012: paths→InputPaths, out→OutputContext, config→RdeConfig."""
        from rdetoolkit.core.context import get_reserved_mapping  # noqa: PLC0415
        from rdetoolkit.types import InputPaths, OutputContext  # noqa: PLC0415

        mapping = get_reserved_mapping()

        assert mapping.get("paths") is InputPaths, (
            f"'paths' must map to InputPaths, got {mapping.get('paths')}"
        )
        assert mapping.get("out") is OutputContext, (
            f"'out' must map to OutputContext, got {mapping.get('out')}"
        )
        config_type = mapping.get("config")
        assert config_type is not None, (
            "'config' key must be present with a type value in the reserved mapping"
        )
        assert config_type.__name__ == "RdeConfig", (
            f"'config' must map to RdeConfig, got {config_type!r}"
        )


# ---------------------------------------------------------------------------
# TC-TYPES-013: RunContext.config slot
# ---------------------------------------------------------------------------


class TestRunContextConfigSlot:
    """RunContext must carry a config slot for RdeConfig per Design §4.1."""

    def test_run_context_has_config_slot__tc_types_013(self) -> None:
        """TC-TYPES-013: 'config' appears in RunContext.__slots__."""
        from rdetoolkit.core.context import RunContext  # noqa: PLC0415

        assert "config" in RunContext.__slots__, (
            f"RunContext must have a 'config' slot. "
            f"Current slots: {RunContext.__slots__}"
        )


# ---------------------------------------------------------------------------
# TC-TYPES-014/015: Documented exclusions from v1 RdeOutputResourcePath
# These are compat anchors — expected to PASS already in Red phase.
# ---------------------------------------------------------------------------


class TestOutputContextDocumentedExclusions:
    """Excluded v1 fields must NOT appear on OutputContext (Design §4.2 + decisions §A2)."""

    def test_rawfiles_is_not_a_field_of_output_context__tc_types_014(self) -> None:
        """TC-TYPES-014 (anchor): rawfiles excluded — it is an input concept, not an output dir.

        Per decisions_pre_A1.md §A2: rawfiles is a tuple[Path,...] of input file references.
        v2 models this via InputPaths or IterationInfo, not OutputContext.
        """
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert not hasattr(OutputContext, "rawfiles"), (
            "OutputContext must NOT have 'rawfiles'. "
            "It is an input-side concept handled by InputPaths / IterationInfo."
        )

    def test_temp_is_not_a_field_of_output_context__tc_types_015(self) -> None:
        """TC-TYPES-015 (anchor): temp excluded — not in the canonical 10 dirs.

        Per decisions_pre_A1.md §A2: the 'temp' directory is not part of Design §4.2's
        10-dir canonical set. v2 users use the standard library tempfile module instead.
        """
        from rdetoolkit.types import OutputContext  # noqa: PLC0415

        assert not hasattr(OutputContext, "temp"), (
            "OutputContext must NOT have 'temp'. "
            "Not in the canonical 10 dirs; use the standard tempfile module."
        )

"""Tests for ``rdetoolkit init --processing-template`` and the bare-``init``
byte-identity golden (Session F2, TC-CLI-INIT-TPL-*).

Written before implementation (TDD Red phase). Authority:
local/develop/v2/tasks/session_f2.md Conflict #1 (RULING: the flag is
``--processing-template <name>``, NOT a second, colliding ``--template``),
Known Trap #8; Design.md v2.1 §5.2.4, §13.3.

Binding API-shape pins asserted by this file (precision standard):
- ``init --processing-template <name> --module <dotted>`` (repeatable
  ``--module``, mirroring ``nodes_cmd.py``'s convention) generates a
  TODO-annotated skeleton file (containing the declared slot names) plus a
  sample test file using ``rdetoolkit.testing.plugin``'s §13 fixtures
  (``rde_paths``/``rde_out``/etc.) -- Design §5.2.4/§13.3's "init して、TODO
  を 2 箇所埋めて、run" day-one experience.
- Unknown ``<name>`` (not found among the ``--module``-imported module's
  Template Registry registrations) is a usage error, exit 3.
- ``init``'s existing v1 ``--template <Path>`` option (with its
  ``exists=True`` Path semantics) is COMPLETELY untouched -- both options
  coexist in ``--help`` output, and passing a nonexistent path to
  ``--template`` still fails with typer's own Path-existence validation
  (exit code 2, Click's default BadParameter code -- NOT this session's
  usage-error convention of exit 3, because this path never reaches
  application code at all).
- Bare ``init`` (no flags) is byte-identical, in both generated file tree
  AND (path-normalized) stdout, to a snapshot captured on THIS WORKTREE'S
  PRE-F2 HEAD (``1a15f56``) by the tdd-enforcer session that wrote this
  file -- never hand-written (Known Trap #8). The frozen snapshot lives at
  ``tests/v2/cli/fixtures/golden_init_bare/``.

FIX-2 EP/BV table:
- TC-CLI-INIT-TPL-OVERWRITE-001: existing ``processing.py`` is rejected
  before any sample test is written.
- TC-CLI-INIT-TPL-OVERWRITE-002: existing ``tests/test_processing.py`` is
  rejected before any processing module is written.
- TC-CLI-INIT-TPL-OVERWRITE-003: when both outputs exist, neither is changed.
- TC-CLI-INIT-TPL-OVERWRITE-004: ``--force`` explicitly replaces both outputs.
- TC-CLI-INIT-TPL-OVERWRITE-005: ``--force`` is discoverable in init help.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rdetoolkit.cli.app import app

FIXTURE_MODULE = "tests.v2.templates.fixtures.xrd_like_template"
GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden_init_bare"
GOLDEN_TREE = GOLDEN_DIR / "tree"
GOLDEN_OUTPUT_TEMPLATE = (GOLDEN_DIR / "output_template.txt").read_text(encoding="utf-8")

_IGNORED_FILENAMES = {".gitkeep"}
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def isolated_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _collect_dirs(root: Path) -> set[str]:
    return {str(p.relative_to(root).as_posix()) for p in root.rglob("*") if p.is_dir()}


def _collect_files(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root).as_posix()): p.read_text(encoding="utf-8")
        for p in root.rglob("*")
        if p.is_file() and p.name not in _IGNORED_FILENAMES
    }


def _normalize_help_output(output: str) -> str:
    without_ansi = _ANSI_ESCAPE_RE.sub("", output)
    return re.sub(r"\s+", "", without_ansi)


class TestBareInitMatchesPreF2Golden:
    """TC-CLI-INIT-TPL-GOLDEN-001/002 (Known Trap #8, Conflict #1's
    byte-identity requirement)."""

    def test_bare_init_produces_the_pre_f2_golden_tree(self, cli_runner: CliRunner, isolated_root: Path) -> None:
        result = cli_runner.invoke(app, ["init"])

        assert result.exit_code == 0, result.output
        assert _collect_dirs(isolated_root) == _collect_dirs(GOLDEN_TREE)
        assert _collect_files(isolated_root) == _collect_files(GOLDEN_TREE)

    def test_bare_init_produces_the_pre_f2_golden_output(self, cli_runner: CliRunner, isolated_root: Path) -> None:
        result = cli_runner.invoke(app, ["init"])

        assert result.exit_code == 0, result.output
        normalized_output = result.output.replace(str(isolated_root), "{ROOT}")
        assert normalized_output == GOLDEN_OUTPUT_TEMPLATE

    def test_init_with_only_preexisting_v1_flags_still_exits_0(self, cli_runner: CliRunner, isolated_root: Path) -> None:
        # A pre-existing v1 sibling flag (--tasksupport requires an
        # existing path; reuse a directory this same test creates) must
        # remain fully functional -- Conflict #1 forbids any behavioral
        # change to init's pre-existing option handling.
        tasksupport_dir = isolated_root / "custom_tasksupport"
        tasksupport_dir.mkdir()
        (tasksupport_dir / "note.txt").write_text("v1 sibling flag payload", encoding="utf-8")

        result = cli_runner.invoke(app, ["init", "--tasksupport", str(tasksupport_dir)])

        assert result.exit_code == 0, result.output


class TestV1TemplateOptionUntouched:
    """TC-CLI-INIT-TPL-V1-001/002 (Conflict #1: --template <Path> and
    --processing-template <name> must coexist without collision)."""

    def test_v1_template_path_option_still_present_in_help(self, cli_runner: CliRunner) -> None:
        # Given: deterministic terminal settings for the init help renderer
        # When: requesting help that includes the pre-existing v1 option
        result = cli_runner.invoke(app, ["init", "--help"], env={"NO_COLOR": "1", "COLUMNS": "200"})

        # Then: ANSI styling and wrapping cannot hide the unchanged option name
        assert result.exit_code == 0
        assert "--template" in _normalize_help_output(result.output)

    def test_v1_template_option_still_enforces_path_existence(self, cli_runner: CliRunner, isolated_root: Path) -> None:
        result = cli_runner.invoke(app, ["init", "--template", str(isolated_root / "does_not_exist")])

        # typer's own Path(exists=True) validation rejects this before
        # application code runs at all -- Click's default BadParameter
        # exit code (2), distinct from this session's usage-error
        # convention (3) used by --processing-template's own validation.
        assert result.exit_code == 2

    def test_processing_template_option_appears_in_help(self, cli_runner: CliRunner) -> None:
        # Given: deterministic terminal settings for the init help renderer
        # When: requesting help that includes the v2 processing-template option
        result = cli_runner.invoke(app, ["init", "--help"], env={"NO_COLOR": "1", "COLUMNS": "200"})

        # Then: ANSI styling and wrapping cannot hide the complete option name
        assert result.exit_code == 0
        assert "--processing-template" in _normalize_help_output(result.output)

    def test_force_option_appears_in_help__tc_cli_init_tpl_overwrite_005(self, cli_runner: CliRunner) -> None:
        # Given: deterministic terminal settings for the init help renderer
        # When: requesting help for processing-template generation controls
        result = cli_runner.invoke(app, ["init", "--help"], env={"NO_COLOR": "1", "COLUMNS": "200"})

        # Then: explicit overwrite consent is discoverable
        assert result.exit_code == 0
        assert "--force" in _normalize_help_output(result.output)


class TestInitProcessingTemplateGeneratesSkeleton:
    """TC-CLI-INIT-TPL-EP-001, TC-CLI-INIT-TPL-BV-001."""

    def test_generates_todo_skeleton_and_sample_test_using_testing_fixtures__tc_cli_init_tpl_ep_001(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DemoSkeletonTemplate", "--module", FIXTURE_MODULE],
        )

        assert result.exit_code == 0, result.output

        generated_py_files = list(isolated_root.rglob("*.py"))
        assert generated_py_files, "init --processing-template must generate at least one .py file"
        combined_source = "\n".join(p.read_text(encoding="utf-8") for p in generated_py_files)

        # TODO-annotated, naming the declared slots (Design §5.2.4).
        assert "TODO" in combined_source
        assert "read" in combined_source
        assert "extract_meta" in combined_source

        # A sample test using the §13 rdetoolkit.testing.plugin fixtures
        # must be generated alongside the skeleton (Design §13.3).
        sample_test_files = [p for p in generated_py_files if p.name.startswith("test_")]
        assert sample_test_files, "init --processing-template must also generate a sample test file"
        sample_source = "\n".join(p.read_text(encoding="utf-8") for p in sample_test_files)
        assert "rde_paths" in sample_source or "rde_out" in sample_source

    def test_unknown_processing_template_name_exits_3__tc_cli_init_tpl_bv_001(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DefinitelyNotARegisteredTemplateName", "--module", FIXTURE_MODULE],
        )

        assert result.exit_code == 3


class TestInitProcessingTemplateOverwriteProtection:
    """FIX-2 overwrite preflight and explicit-consent cases."""

    def test_existing_processing_module_is_rejected_before_sample_write__tc_cli_init_tpl_overwrite_001(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        # Given: a user-owned processing module and no sample test
        processing_path = isolated_root / "processing.py"
        processing_path.write_text("USER PROCESSING\n", encoding="utf-8")

        # When: generating without explicit overwrite consent
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DemoSkeletonTemplate", "--module", FIXTURE_MODULE],
        )

        # Then: generation is rejected without changing or partially creating files
        assert result.exit_code == 3
        assert "--force" in result.stderr
        assert "overwrite" in result.stderr.lower()
        assert processing_path.read_text(encoding="utf-8") == "USER PROCESSING\n"
        assert not (isolated_root / "tests" / "test_processing.py").exists()

    def test_existing_sample_test_is_rejected_before_processing_write__tc_cli_init_tpl_overwrite_002(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        # Given: a user-owned sample test and no processing module
        test_path = isolated_root / "tests" / "test_processing.py"
        test_path.parent.mkdir()
        test_path.write_text("USER TEST\n", encoding="utf-8")

        # When: generating without explicit overwrite consent
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DemoSkeletonTemplate", "--module", FIXTURE_MODULE],
        )

        # Then: generation is rejected without changing or partially creating files
        assert result.exit_code == 3
        assert "--force" in result.stderr
        assert "overwrite" in result.stderr.lower()
        assert test_path.read_text(encoding="utf-8") == "USER TEST\n"
        assert not (isolated_root / "processing.py").exists()

    def test_existing_outputs_are_both_unchanged__tc_cli_init_tpl_overwrite_003(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        # Given: both generated paths already contain user-owned content
        processing_path = isolated_root / "processing.py"
        test_path = isolated_root / "tests" / "test_processing.py"
        test_path.parent.mkdir()
        processing_path.write_text("USER PROCESSING\n", encoding="utf-8")
        test_path.write_text("USER TEST\n", encoding="utf-8")

        # When: generation is requested without --force
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DemoSkeletonTemplate", "--module", FIXTURE_MODULE],
        )

        # Then: the preflight rejects before either write begins
        assert result.exit_code == 3
        assert processing_path.read_text(encoding="utf-8") == "USER PROCESSING\n"
        assert test_path.read_text(encoding="utf-8") == "USER TEST\n"

    def test_force_replaces_both_existing_outputs__tc_cli_init_tpl_overwrite_004(
        self,
        cli_runner: CliRunner,
        isolated_root: Path,
    ) -> None:
        # Given: both generated paths already contain user-owned content
        processing_path = isolated_root / "processing.py"
        test_path = isolated_root / "tests" / "test_processing.py"
        test_path.parent.mkdir()
        processing_path.write_text("USER PROCESSING\n", encoding="utf-8")
        test_path.write_text("USER TEST\n", encoding="utf-8")

        # When: generation is requested with explicit overwrite consent
        result = cli_runner.invoke(
            app,
            ["init", "--processing-template", "DemoSkeletonTemplate", "--module", FIXTURE_MODULE, "--force"],
        )

        # Then: both outputs are regenerated together
        assert result.exit_code == 0, result.output
        assert processing_path.read_text(encoding="utf-8") != "USER PROCESSING\n"
        assert test_path.read_text(encoding="utf-8") != "USER TEST\n"

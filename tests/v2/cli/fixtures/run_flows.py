"""Fixture flows/nodes for ``rdetoolkit run --flow`` CLI tests (Session E1).

These are real, module-scope ``@node``/``@flow`` definitions living in an
actual dotted-importable package (``tests.v2.cli.fixtures.run_flows``) --
required because Conflict #11 (session_e1.md) restricts ``--flow``
resolution to ``importlib.import_module(<dotted pkg.mod>)`` + ``getattr``,
with no file-path support (unlike the legacy ``target::attr`` syntax).

Each pipeline below is used by exactly one or two TC-CLI-RUN-* cases in
``tests/v2/cli/test_cli_run.py`` -- see that file's module docstring for the
mapping. Node ids are explicit (``@node(id=...)``) so re-imports across the
pytest session never collide (module import is cached by Python, so
decorators here execute exactly once regardless of how many CLI
invocations resolve this module).
"""

from __future__ import annotations

from rdetoolkit.core.flow import flow
from rdetoolkit.core.node import node
from rdetoolkit.types import InputPaths, IterationInfo

# TC-CLI-RUN-EP-009/EP-010: appended to by validate_only_pipeline. Must
# remain empty after any ``run --flow ... --validate-only`` invocation --
# this is the E1.3-mandated side-effect sentinel (Conflict #3). Tests must
# snapshot ``len(VALIDATE_ONLY_SENTINEL)`` before invoking the CLI and
# assert it is unchanged afterward (module-level list persists across the
# whole pytest session, so a bare emptiness check is not reliable on its
# own if some other test happens to invoke this same pipeline for a
# real, non-validate-only run in the future).
VALIDATE_ONLY_SENTINEL: list[str] = []


@node(id="e1_cli_fixture_touch_success")
def _touch_success(paths: InputPaths) -> None:
    return None


@flow(id="e1_cli_fixture_success_pipeline")
def success_pipeline(paths: InputPaths) -> None:
    """TC-CLI-RUN-EP-001: every tile succeeds unconditionally."""
    _touch_success(paths)


@node(id="e1_cli_fixture_touch_always_fail")
def _touch_always_fail(paths: InputPaths) -> None:
    msg = "e1_cli_fixture_touch_always_fail: intentional failure"
    raise RuntimeError(msg)


@flow(id="e1_cli_fixture_failing_pipeline")
def failing_pipeline(paths: InputPaths) -> None:
    """TC-CLI-RUN-EP-003: every tile fails unconditionally (single-tile
    invoice-mode fixture -> completed_count == 0 -> RunReport.status ==
    "failed" regardless of the on_iteration_error policy)."""
    _touch_always_fail(paths)


@node(id="e1_cli_fixture_touch_second_tile")
def _touch_second_tile(paths: InputPaths, iteration: IterationInfo) -> None:
    if iteration.index == 1:
        msg = "e1_cli_fixture_touch_second_tile: intentional failure on tile index 1"
        raise RuntimeError(msg)


@flow(id="e1_cli_fixture_second_tile_fails_pipeline")
def second_tile_fails_pipeline(paths: InputPaths, iteration: IterationInfo) -> None:
    """TC-CLI-RUN-EP-002/EP-012: first of two tiles succeeds, second always
    fails. Under the default ``on_iteration_error="continue"`` this yields
    RunReport.status == "partial"; under an ``execution.on_iteration_error:
    fail_fast`` override it yields "failed" (EP-012's observable
    --config-changes-the-outcome proof)."""
    _touch_second_tile(paths, iteration)


@node(id="e1_cli_fixture_touch_validate_only_sentinel")
def _touch_validate_only_sentinel(paths: InputPaths) -> None:
    VALIDATE_ONLY_SENTINEL.append("called")


@flow(id="e1_cli_fixture_validate_only_pipeline")
def validate_only_pipeline(paths: InputPaths) -> None:
    """TC-CLI-RUN-EP-009/EP-010: appends to VALIDATE_ONLY_SENTINEL when
    actually called. ``run --flow ... --validate-only`` must NEVER call
    this flow (Conflict #3) -- the sentinel must stay unchanged."""
    _touch_validate_only_sentinel(paths)


class NotAFunctionTarget:
    """TC-CLI-RUN-EP-006: a plain, undecorated class target. ``--flow``
    resolving to a class (not a function) must be rejected as a usage
    error referencing Phase F / ProcessingTemplate (Conflict #11) -- this
    session implements no template-class handling at all.
    """

"""Executed examples for the v1-to-v2 migration guide.

EP table
========

====================  ======================  =============================  ====================
Example               Partition               Expected                       Test ID
====================  ======================  =============================  ====================
migration commands    check and dry-run apply commands accepted by CLI       TC-DOC-MIG-EP-001
``as_node`` bridge    legacy handler method  callable node preserves result TC-DOC-MIG-EP-002
====================  ======================  =============================  ====================

BV table
========

====================  ======================  =============================  ====================
Example               Boundary                Expected                       Test ID
====================  ======================  =============================  ====================
documentation fences  every fenced example   marker and execution coverage TC-DOC-MIG-BV-001
====================  ======================  =============================  ====================
"""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from rdetoolkit.cli.app import app

DOC = Path(__file__).parents[3] / "docs" / "migration_v1_to_v2.md"
EXAMPLE_RE = re.compile(r"<!-- test: (?P<name>[\w-]+) -->\n```(?P<language>\w+)\n(?P<code>.*?)```", re.DOTALL)


def _examples() -> dict[str, tuple[str, str]]:
    text = DOC.read_text(encoding="utf-8")
    examples = {
        match.group("name"): (match.group("language"), match.group("code"))
        for match in EXAMPLE_RE.finditer(text)
    }
    assert text.count("```") == 2 * len(examples), "Every fenced example must have a test marker"
    return examples


def test_migration_cli_commands_execute__tc_doc_mig_ep_001(tmp_path: Path, monkeypatch) -> None:
    """TC-DOC-MIG-EP-001: documented migration commands execute through the public CLI."""
    # Given: the documented legacy source and command sequence
    examples = _examples()
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "legacy.py"
    source.write_text(examples["legacy-source"][1], encoding="utf-8")
    commands = [line.removeprefix("$ ").split() for line in examples["migration-commands"][1].splitlines()]
    # When: each documented python -m rdetoolkit command is invoked
    results = [CliRunner().invoke(app, command[3:]) for command in commands]
    # Then: check and the default dry-run apply both succeed without writing output
    assert all(result.exit_code == 0 for result in results), [result.output for result in results]
    assert not source.with_name("legacy_migrated").exists()


def test_as_node_bridge_executes__tc_doc_mig_ep_002() -> None:
    """TC-DOC-MIG-EP-002: the migration-only as_node bridge example is executable."""
    # Given: the complete documented bridge example
    namespace: dict[str, object] = {}
    # When: executing it as ordinary Python
    exec(_examples()["as-node-bridge"][1], namespace)  # noqa: S102
    # Then: the example's own assertion ran and produced the documented value
    assert namespace["result"] == "SAMPLE.TXT"


def test_every_migration_fence_is_executed__tc_doc_mig_bv_001() -> None:
    """TC-DOC-MIG-BV-001: no unmarked migration-guide code fence can bypass execution."""
    # Given: all fenced examples in the migration guide
    examples = _examples()
    # When: comparing their stable marker names with this module's executed set
    executed = {"legacy-source", "migration-commands", "as-node-bridge"}
    # Then: every example is explicitly owned by an execution test
    assert set(examples) == executed

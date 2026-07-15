"""Tests for rdetoolkit v2 builtin metadata nodes (Session F1.4,
TC-F1-META-*).

Written before implementation (TDD Red phase). Target: make all tests pass
in codex-worker Green phase. Authority: local/develop/v2/tasks/session_f1.md
Conflict #2 (argument order: ``save_meta(metadata: Metadata, out:
OutputContext) -> Path`` is the pinned literal example), Conflict #9
(invalid-input exception choice: v1's ``StructuredError`` OR a plain
``ValueError`` -- Codex's choice, this file accepts either).

Pinned API shapes (binding contract for this file):

    parse_invoice_meta(invoice: InvoiceData, metadef_path: Path) -> Metadata
    save_meta(metadata: Metadata, out: OutputContext) -> Path

Porting source: ``rdetoolkit.rde2util.Meta`` (``__init__``/``assign_vals``).
This test file's ``metadata-def.json`` fixture and its EP/BV invoice payloads
were independently verified directly against ``rde2util.Meta`` before being
pinned here as node-level oracles (see the tdd-enforcer session transcript):

    - EP: ``Meta(metadef_path).assign_vals({"sample.key1": "value1",
      "sample.key2": 42})`` succeeds and assigns both keys.
    - BV: adding ``"sample.derived"`` (an action-derived key in the fixture
      metadata-def) directly to the input dict makes
      ``Meta.assign_vals`` raise ``StructuredError("ERROR: this meta value
      should set by action")`` -- a real v1 contract violation, not an
      invented one.

``parse_invoice_meta`` is expected to raise on the same underlying condition
when it encounters ``sample.derived`` directly in ``invoice.raw`` (Conflict
#9: propagating v1's ``StructuredError`` or raising a documented
``ValueError`` are both acceptable; this file's BV test accepts either).
"""
from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.testing.builders import make_invoice
from rdetoolkit.types import Metadata, OutputContext
from tests.v2.nodes.conftest import FIXTURES_DIR


def _json_tree_contains_pair(obj: Any, key: str, value: Any) -> bool:
    """Recursively search a decoded JSON value for a matching key/value pair
    anywhere in the structure (the exact top-level JSON schema for saved
    metadata is Codex's implementation choice, per this session's Conflict
    resolutions -- this helper avoids over-pinning that shape)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key and (v == value or str(v) == str(value)):
                return True
            if _json_tree_contains_pair(v, key, value):
                return True
        return False
    if isinstance(obj, list):
        return any(_json_tree_contains_pair(item, key, value) for item in obj)
    return False


class TestParseInvoiceMeta:
    """TC-F1-META-PARSE-*."""

    def test_valid_invoice_produces_metadata_with_assigned_custom_fields(self) -> None:
        """EP: a valid invoice + metadata-def.json fixture pair produces a
        Metadata instance whose custom fields include the assigned values
        (mirrors Meta.assign_vals)."""
        from rdetoolkit.nodes.meta import parse_invoice_meta

        invoice = make_invoice({"sample.key1": "value1", "sample.key2": 42})

        result = parse_invoice_meta(invoice, FIXTURES_DIR / "metadata-def.json")

        assert isinstance(result, Metadata)
        assert result.custom.get("sample.key1") == "value1"
        assert str(result.custom.get("sample.key2")) == "42"

    def test_invoice_value_violating_metadef_action_contract_raises(self) -> None:
        """BV (Conflict #9): an invoice directly assigning a value to an
        action-derived metadata-def key violates the v1 contract and raises
        (StructuredError, propagated from rde2util.Meta, or a documented
        plain ValueError -- Codex's choice)."""
        from rdetoolkit.nodes.meta import parse_invoice_meta

        invoice = make_invoice({"sample.key1": "value1", "sample.derived": "not-allowed"})

        with pytest.raises((StructuredError, ValueError)):
            parse_invoice_meta(invoice, FIXTURES_DIR / "metadata-def.json")

    def test_nonexistent_metadef_path_raises(self) -> None:
        """BV: a nonexistent metadata-def.json path raises."""
        from rdetoolkit.nodes.meta import parse_invoice_meta

        invoice = make_invoice({"sample.key1": "value1"})

        with pytest.raises(OSError):
            parse_invoice_meta(invoice, FIXTURES_DIR / "definitely_missing_metadata_def.json")

    def test_registered_as_builtin_node(self) -> None:
        """Registration: parse_invoice_meta appears in the registry after import."""
        import rdetoolkit.nodes  # noqa: F401
        from rdetoolkit.core import registry

        ids = {spec.id for spec in registry.list_nodes()}
        assert any(node_id.endswith("parse_invoice_meta") for node_id in ids), ids


class TestSaveMeta:
    """TC-F1-META-SAVE-*."""

    def test_writes_json_file_under_out_meta(self, output_context: OutputContext) -> None:
        """EP: a Metadata instance is written as a JSON file under out.meta."""
        from rdetoolkit.nodes.meta import save_meta

        metadata = Metadata(custom={"sample.key1": "value1"})

        result_path = save_meta(metadata, output_context)

        assert result_path.exists()
        assert result_path.parent == output_context.meta
        assert result_path.suffix == ".json"
        decoded = json.loads(result_path.read_text(encoding="utf-8"))
        assert _json_tree_contains_pair(decoded, "sample.key1", "value1")

    def test_delegates_to_output_context_write_api(self) -> None:
        """Delegation guard: save_meta's source calls write_bytes or path_for."""
        from rdetoolkit.nodes.meta import save_meta

        source = inspect.getsource(save_meta)
        assert "write_bytes" in source or "path_for" in source

    def test_registered_as_builtin_node(self) -> None:
        """Registration: save_meta appears in the registry after import."""
        import rdetoolkit.nodes  # noqa: F401
        from rdetoolkit.core import registry

        ids = {spec.id for spec in registry.list_nodes()}
        assert any(node_id.endswith("save_meta") for node_id in ids), ids


class TestParseInvoiceMetaThenSaveMetaRoundTrip:
    """Integration: TC-F1-META-ROUNDTRIP-001."""

    def test_parse_then_save_round_trip_is_readable_back(self, output_context: OutputContext) -> None:
        """parse_invoice_meta -> save_meta round-trip produces a file whose
        decoded JSON still contains the originally-assigned values."""
        from rdetoolkit.nodes.meta import parse_invoice_meta, save_meta

        invoice = make_invoice({"sample.key1": "value1", "sample.key2": 42})
        metadata = parse_invoice_meta(invoice, FIXTURES_DIR / "metadata-def.json")

        result_path = save_meta(metadata, output_context)
        decoded = json.loads(result_path.read_text(encoding="utf-8"))

        assert _json_tree_contains_pair(decoded, "sample.key1", "value1")
        assert _json_tree_contains_pair(decoded, "sample.key2", 42)

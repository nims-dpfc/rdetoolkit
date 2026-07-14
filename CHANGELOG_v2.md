# rdetoolkit v2 changelog

## Phase F — migration protocol alignment

The unreleased pre-v2.1 protocol surface was replaced by the migration-only
contracts in Design Appendix M:

- Removed `DataValidator`, `NodeRunner`, and `FormatHandler`.
- Changed `FileReader.read` from `read(path: str) -> bytes` to the canonical
  `InputPaths -> tuple[Metadata, DataFrame]` contract.
- Changed `MetadataExtractor.extract` from a bytes/dict placeholder to the
  canonical `(DataFrame, InvoiceData) -> Metadata` contract.
- Added `DataProcessor`, `ResultWriter`, and `Visualizer`.

These protocols are migration aids only. New code should use processing
templates (Design §5.2) or plain node/flow functions (Design §3).

## Phase F — plugin discovery and migration application

- Added declarative discovery for plugin-provided nodes, format handlers, and
  processing templates, with provenance-aware inspection commands and
  warn-and-skip handling for broken third-party entry points.
- Added `formats list`, `nodes list --plugin`, and automatic plugin discovery
  for `templates list`; Runner lifecycle extension points remain intentionally
  unavailable (Design §5.3).
- Completed the level-3 `testing.run_flow` contract for function and template
  targets, including recursive fixture trees (Design §13).
- Added dry-run-first `migrate apply`, external-only output, explicit TODO
  markers for unresolved constructs, and a five-template corpus demonstrating
  the ADR-021 80% executable-conversion condition.

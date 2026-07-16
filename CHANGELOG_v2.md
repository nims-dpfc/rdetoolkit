# rdetoolkit v2 changelog

## 2.0.0a1 — 2026-07-14

This alpha is the Phase F feature baseline. It keeps the current dual-entry
runtime as a canary and rollback point while unified-runner work continues;
the public v2 result model is `RunReport`.

The release is identified by the git tag `v2.0.0a1`, while the in-code version
remains `2.0.0` for now because the v1 ExcelInvoice template embeds a version
whose format contract accepts only stable `X.Y.Z`. Relaxing that contract will
ship in an independent PR to `main` before the first release candidate.

### Added

- Eager `@node` and `@flow` execution with runtime call-log recording and
  post-run call-sequence reports.
- RDE Runner lifecycle, five registration modes, validation, iteration error
  policies, Events, `RunReport`, `job.failed`, report/graph/repro commands, and
  testing fixtures.
- Fifteen canonical builtin nodes for input, structured output, metadata,
  images, and plots.
- `ProcessingTemplate`, required slots, template discovery, `templates`
  commands, and `init --processing-template` skeleton generation.
- Declarative plugin discovery for node sets, format handlers, and processing
  templates; `formats list` and `nodes list --plugin`.
- Dry-run-first `migrate check` / `migrate apply` and the level-3
  `rdetoolkit.testing.run_flow` helper.
- Generated error-catalog documentation, an executed progressive tutorial,
  and a provisional v1-to-v2 migration guide.

### Compatibility notes

- v2 flow executions return `RunReport`.
- `on_iteration_error` defaults to `continue`; select `fail_fast` explicitly
  when immediate termination is required.
- Runtime unification and final compatibility commitments are scheduled after
  this alpha and before the release candidate.

### Changed — migration protocol alignment

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

### Added — plugin discovery and migration application

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

### Fixed — Phase F review remediation

- Made rich-rendered `init --help` assertions robust to ANSI styling and line
  wrapping in color-enabled CI environments.
- Prevented `init --processing-template` from overwriting generated files
  unless the user explicitly supplies `--force`.
- Restricted template execution to registered depth-2 concrete classes and
  registered inherited default hooks under each concrete class's node id.
- Derived plugin node/template provenance from loaded provider objects so
  discovery remains correct after pre-import.
- Read `migrate apply` inputs with their PEP 263 declared encoding and report
  malformed files without aborting sibling conversions.

### Added — Phase G unified-runner contracts

- Added the seven v1 artifact-behavior settings to strict `RdeConfig` with
  v1-identical defaults, including a dedicated `smarttable` section.
- Added immutable `FlowTarget`, `LegacyCallbackTarget`, and `RunRequest`
  boundary types plus entry-point normalization using catalog error 1001.
- Fixed the Phase H contracts for legacy config normalization and explicit
  `RunReport.to_legacy_statuses()` conversion against frozen v1 fixtures.

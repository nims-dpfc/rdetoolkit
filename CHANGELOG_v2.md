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

### Fixed — Phase G contract review remediation

- Made flat-layout ExcelInvoice backup root-relative and independent of the
  process working directory, with the same parsed JSON content as its source.
- Recreated Git-unrepresentable empty staging directories during oracle-case
  materialization and covered fresh-checkout behavior with a regression test.
- Strengthened all 16 frozen v1 observations with parsed invoice-backup content
  and complete normalized `job.failed` text.
- Normalized the order-dependent RDEFormat status-target subdirectory while
  retaining each deterministic `data/temp/NNNN` tile prefix.

### Changed — Phase H Runner lifecycle completion

- Completed source invoice pre-validation and the completed-tile output sweep
  by delegating to the existing `invoice_validate` and `metadata_validate`
  domain functions. Missing metadata remains an optional, v1-compatible skip.
- Defined output-validation failures as run-level failures: an invalid
  completed invoice now produces catalog code 4001 and `job.failed`; artifacts
  left by failed iterations are excluded from the sweep.
- Split execution planning, tile execution, flow invocation, and finalization
  into `RunPlanner`, `TileExecutor`, `FlowInvoker`, and `RunFinalizer` while
  preserving the six public `Runner` lifecycle step methods.

### Changed — Phase H Runner lifecycle completion

- Completed source invoice pre-validation and the completed-tile output sweep
  by delegating to the existing `invoice_validate` and `metadata_validate`
  domain functions. Missing metadata remains an optional, v1-compatible skip.
- Defined output-validation failures as run-level failures: an invalid
  completed invoice now produces catalog code 4001 and `job.failed`; artifacts
  left by failed iterations are excluded from the sweep.
- Split execution planning, tile execution, flow invocation, and finalization
  into `RunPlanner`, `TileExecutor`, `FlowInvoker`, and `RunFinalizer` while
  preserving the six public `Runner` lifecycle step methods.
- Recorded the executing `git describe --always --dirty` revision in generated
  snapshots and added non-failing provenance warnings plus deterministic input
  drift checks; XLSX drift is compared semantically because workbook metadata
  bytes are nondeterministic.

### Changed — Phase H cleanup

- Removed the unused `RunAggregator.record_failure()` method; Runner failure
  paths already record canonical failed `ExecutionResult` instances.

### Added — Phase H request and configuration normalization

- Relocated the unchanged v1 `rdetoolkit.config` module into a compatible
  package and added strict v1/v2 `ConfigNormalizer` conversion.
- Added the total `RunReport.to_legacy_statuses()` compatibility conversion,
  including a defined status representation for failed runs where v1 exited
  without returning a value.
- Routed v2 flow execution through `RunRequest`, moved ProcessingTemplate
  conversion to request normalization, and kept the v1 callback branch intact.

### Added — Phase H common domain services and concurrent Runner support

- Added path-based `InvoiceService`, `RawArtifactService`,
  `ImageArtifactService`, `OutputLayoutResolver`, `InputValidator`, and
  deterministic `IterationFactory` services, consuming all seven canonical v1
  artifact settings without routing through legacy mode processors.
- Replaced cwd-relative invoice backup with one explicit-root implementation
  and replaced process-wide SmartTable cache clearing with targeted per-root
  invalidation owned by the Runner's invoice service.
- Added two-thread, distinct-root acceptance coverage across all five modes;
  output snapshots, invoice content, and primary RunReport fields match an
  isolated execution.
- Deferred live per-tile wiring of `RawArtifactService` and
  `ImageArtifactService` to Phase I I5/I6 so Phase H does not change existing
  output trees or frozen contracts.

### Fixed — Phase H PR #521 blocker remediation

- Made failed-run finalization resolve both project-root and already-flat
  `data` layouts before writing the absolute `job.failed` path, while retaining
  the unchanged v1 writer and file format.
- Replaced identity serialization in `RunReport.to_legacy_statuses()` with a
  total conversion from primary `RunAggregator` iteration results. Tile
  results now retain title, target, and stacktrace at the execution boundary.
- Bumped `RunReport.schema_version` from `"1"` to `"2"` because the serialized
  iteration schema adds `title`, `target`, and `stacktrace`. Consumers that
  read only existing primary fields remain compatible; schema-aware consumers
  must accept version 2. `rdetoolkit report show` now reads the current schema
  constant instead of hardcoding an older version.
- Classified explicit v1 `Config` instances with `origin="v1"` and preserved
  catalogued `RdeConfigError(1002)` failures instead of exposing Pydantic
  `ValidationError` causes.
- Separated business-lifecycle failure handling from the exactly-once
  finalization boundary. Finalization I/O failures now surface as catalogued
  `RdeInternalError(5001)` and never trigger a second finalize attempt.
- Enabled branch coverage and added focused rejection, interruption, path,
  artifact-filter, directory-copy, copy-failure, and disabled-image tests for
  new Phase H modules.

#### Existing-test UPDATE table

| Test seat | Previous expectation | Strengthened expectation and reason |
| --- | --- | --- |
| `test_finalize.py` TC-FIN-006 | v1 writer received only code/message | writer must also receive the resolved absolute root-owned filename (F1) |
| `test_legacy_statuses_contract.py` TC-EP-G2-301..315 | expected legacy payload was injected into `RunReport.iterations` | independent frozen invoices/output inventory produce real `ExecutionResult` → `RunAggregator` output before exact legacy comparison (F2; removes tautology) |
| `test_aggregator.py` TC-AGG-001 | five-field iteration summary | summary explicitly retains compatibility title/target/stacktrace (F2 schema 2) |
| `test_iteration_streaming.py` TC-D2R-F5 | five-field canonical summary | serialized iteration schema 2 includes the three explicit compatibility inputs (F2) |
| `test_execute.py` TC-EXEC-001 | six-field `ExecutionResult` | execution result explicitly carries title/target/stacktrace while they are available (F2) |
| `test_run_report.py` TC-EP-001/002 | schema version 1 | schema version 2 is asserted after the serialized iteration change (F2) |
| `test_run_flow.py` TC-E2E-004 | schema version 1 | end-to-end report asserts schema version 2 (F2) |
| `test_event_schema.py` TC-EVENT-022 helper/assertion | schema version 1 | schema-aware serialization seat asserts version 2 (F2) |
| `test_config_loader.py` TC-CFG-005/006 | raw Pydantic `ValidationError` | public `RdeConfigError` with integer code 1002 (F4 contract strengthening) |
| `test_rdeconfig_v1_keys.py` TC-EP-G2-005 | direct model `ValidationError` | public loader rejects every strict-section unknown key with `RdeConfigError(1002)` (F4) |
| `test_cli_report.py` TC-CLI-REPORT-EP-003 fixture | version-1 report was current | version-2 report is current and must not emit an unknown-schema warning (F2 consumer compatibility) |

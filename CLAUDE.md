# CLAUDE.md

This file provides Claude Code-specific guidance when working with code in this repository.

> **📋 Development Rules**: For comprehensive development rules (testing methodology,
> code style, language boundary, branch strategy, environment setup), see
> **[AGENTS.md](./AGENTS.md)**. This file focuses on Claude Code-specific guidance,
> architecture, agent usage patterns, and Codex delegation (including `/goal`).

> **⚠️ Canonical design**: `local/develop/v2/Design.md` (eager execution + runtime
> provenance, ADR-020). `Plan.md` and the 2026-02 design note are superseded.
> **Never implement Trace proxies, Build/Compile phases, or pre-execution DAGs** —
> if you remember those from this repo, that is the retired design.

## Quick Reference

- **Testing Requirements** → [AGENTS.md §7](./AGENTS.md#7-testing)
- **Language Boundary / dag.rs freeze** → [AGENTS.md §4](./AGENTS.md#4-rust--python-language-boundary)
- **Code Style & Standards** → [AGENTS.md §3](./AGENTS.md#3-code-formatting--linters)
- **Branch Strategy** → [AGENTS.md §6](./AGENTS.md#6-branch-strategy)
- **Forbidden Actions** → [AGENTS.md §8.2](./AGENTS.md#82-forbidden-actions)

---

## Project Overview

RDEToolKit is a Python package for creating workflows of RDE (Research Data Express)
structured programs. The project is a **Rust + Python hybrid library** using
PyO3/Maturin (Rust is v1-only; v2.0 adds no Rust).

### Current Development Status

- **v1.x** — stable, maintenance mode. Bug fixes and minor improvements only.
- **v2.x** — active development, **redesigned 2026-06**.
  - Canonical spec: `local/develop/v2/Design.md`
  - Phase instructions: `local/develop/v2/Phase{A..F}_prompts.md`
  - Branch: `develop/v2`, work on `v2/phase-<a..f>`

---

## Architecture

### v2 Execution Model (eager + provenance)

```
Layer 4:  CLI / Entry Points      rdetoolkit run / nodes / flows / graph / report / repro / migrate
Layer 3:  Runner (Orchestration)  config → mode → validate → iterate tiles → flow call → validate → finalize
Layer 2:  Domain Services         config / mode / validation / paths / invoice
Layer 1:  Node Registry + Provenance   @node / @flow / NodeSpec / NodeCallRecord / flow-boundary DI
Layer 0:  Shared Kernel           types / errors (int catalog) / events (schema_version) / models
```

Key invariants (Design §1):
1. `@flow` runs as **plain Python** — no trace, no compile, no proxies.
2. `@node` = registration + runtime recording + opt-in type check. Directly callable.
3. The DAG is **observed** from provenance, rendered post-hoc (`rdetoolkit graph`).
4. The Runner owns all RDE ceremony incl. the `job.failed` contract and directory
   contract (golden-tested against v1).
5. v1 code path (`run(custom_dataset_function=...)`) is untouched — no bridge.

### Rust Core Modules

| Module | Responsibility | Status |
|--------|---------------|--------|
| `imageutil.rs` | Image processing, thumbnails | v1 (unchanged) |
| `charset_detector.rs` | Encoding detection | v1 (unchanged) |
| `fsops.rs` | File system ops | v1 (unchanged) |
| `dag.rs` | (former v2 DAG engine) | **FROZEN — internal, unregistered, never imported from v2** |

Extension module: `rdetoolkit._core` (stub: `src/rdetoolkit/_core.pyi`).
`maturin develop` is only needed when a v1 Rust file changes.

### v1.x Architecture (Stable — Do Not Break)

1. **Workflow Pipeline** (`workflows.py`, `processing/pipeline.py`) —
   `run(custom_dataset_function=...)`, linear Processor pipeline,
   modes: invoice / excelinvoice / extended (MultiDataTile, SmartTable)
2. **Data Models** (`models/`) — Config (pydantic), invoice schema, paths
3. **CLI** (`cli/`) — init, gen-invoice, gen-excelinvoice, archive

---

## Working with Claude Code Agents

### Agent Roster

#### Orchestration
- **task-decomposer** — Reads `local/develop/v2/Phase{X}_prompts.md`, classifies
  session type, dispatches the correct pipeline. **Entry point for all v2 work.**
- **task-executor** — Executes decomposed tasks via Claude (non-Codex tasks).

#### Implementation
- **codex-worker** — Delegates to Codex (gpt-5.4 xhigh) via the `codex` CLI with a
  **per-session `/goal`** (see "Codex CLI Integration" below). Runs Codex I/O inside
  a subagent context so the main conversation is not flooded.
- **/codex-delegate Skill** (`.claude/skills/codex-delegate/SKILL.md`) — Equivalent
  entry point for main-context delegation. Shares prompt + goal conventions.
- **python-expert** — Complex architectural decisions when delegation isn't appropriate.

#### Quality & Testing
- **tdd-enforcer** — Writes failing test files before implementation
  (`standard` mode for new modules, `v1-reuse` mode when v1 files are touched).
- **quality-checker** — Runs ruff, mypy, full tox suite after each codex round.
  Also verifies the **goal evidence** (see below) before a goal may be completed.

#### Analysis / Refactoring / Git
- **root-cause-analyst**, **performance-engineer**, **refactoring-expert**,
  **system-architect**, **pr-generator** — unchanged roles.

---

## Development Workflows

### v2 Development Workflow (Primary)

Input: `local/develop/v2/Phase{A..F}_prompts.md` (each references Design.md sections)

```
task-decomposer
  └─ Reads PhaseX_prompts.md, classifies each session, generates task files

Session Classification:
  Cleanup / settlement      → Pipeline S  (serial, human checkpoints)   … A3
  New-with-v1-ref           → Pipeline B  (tdd-enforcer → codex-worker) … A2, B*, C*, D*, F*
  Direct Refactor (v1 hit)  → Pipeline C  (v1-reuse baseline → codex-worker, serialized) … A1, D2, E*

Pipeline B:  tdd-enforcer (standard) → codex-worker (+/goal) → quality-checker
Pipeline C:  tdd-enforcer (v1-reuse: confirm v1 GREEN baseline)
               → codex-worker (+/goal, serialized — never parallel with other v1-touching work)
               → quality-checker → full tox (mandatory)
Pipeline S:  Claude-led, step-by-step with human confirmation between A3.1/A3.2/A3.3.
             Deletion-heavy work is NOT delegated to Codex.
```

**Parallelization rule** (unchanged in spirit): group sessions with no v1 impact
into one parallel round; serialize anything that touches v1 files. quality-checker
runs between rounds.

| Phase | Sessions | v1 impact | Default rounds |
|-------|----------|-----------|----------------|
| A | A1, A2, A3 | A1 (errors.pyi), A3 (cleanup) | A1 → A2 → A3 all serial (contracts build on each other) |
| B | B1, B2 | none | B1 → B2 serial (B2 needs B1) |
| C | C1, C2 | none | C1 → C2 serial |
| D | D1, D2 | D2 (workflows.py) | D1 → D2 serial |
| E | E1, E2 | both (cli/) | E1 → E2 serial |
| F | F1, F2 | none | F1 → F2 serial (F2 docs need F1 nodes) |

> Phases themselves are strictly sequential (A → B → C → D → E → F): each phase
> gate requires full suite GREEN and `--no-ff` merge to `develop/v2`.

**Phase branch rule:** Always work on `v2/phase-<letter>`. Never commit to
`develop/v2` directly.

### v1 Maintenance / Bug / Refactoring / PR workflows — unchanged

```
v1 issue:  task-decomposer (issue mode) → task-executor × N → quality-checker
bug:       root-cause-analyst → python-expert → tdd-enforcer (regression) → quality-checker
refactor:  system-architect → task-decomposer → refactoring-expert → quality-checker
PR:        quality-checker (final) → pr-generator
```

---

## Key Files and Their Purposes

### v1.x (Do Not Break)
- `workflows.py` — `run(custom_dataset_function=...)` (D2 adds dispatch only)
- `processing/pipeline.py`, `models/config.py`, `result.py`, `rde2util.py`, `fileops.py`

### v2.x (In Development)
- `local/develop/v2/Design.md` — **canonical architecture spec**
- `local/develop/v2/Phase{A..F}_prompts.md` — session instructions
- `local/develop/v2/goals/` — per-phase `/goal` templates (see below)
- `src/rdetoolkit/core/` — node / flow / registry / provenance / injection / context
- `src/rdetoolkit/runner/` — lifecycle / paths / iterator / execute / aggregator / finalize
- `src/rdetoolkit/report/`, `nodes/`, `protocols/`, `plugin/`, `testing/`, `cli/`
- `tests/v2/` — all v2 tests (never touch `tests/` root)

---

## Testing

See [AGENTS.md §7](./AGENTS.md#7-testing). Summary:

```bash
.venv/bin/tox -e py312-module                      # full suite — the phase gate
.venv/bin/tox -e py312-module -- tests/v2/ -v      # v2 only
.venv/bin/tox -e py312-module -- tests/v2/golden/ -v   # v1↔v2 parity
pytest tests/v2/ -m property -v                    # PBT
```

---

## Codex CLI Integration (with Goals)

v2 implementation is delegated to Codex (gpt-5.4 xhigh) via the `codex` CLI.
**Every delegated session runs under a `/goal`** — a thread-scoped completion
contract that keeps Codex working toward the session's acceptance criteria across
turns, with evidence-based completion.

### Why Goals here

Our sessions are exactly the shape Goals are designed for: a clear finish line
(tox GREEN + checklist), an uncertain path (TDD red/green/refactor loops), and a
strong need for constraint preservation (v1 tests must never go RED, append-only
files, no retired-design code). The goal removes the "keep going / run tox again /
now check ruff" babysitting and replaces it with a contract Codex audits itself
against.

### Requirements & configuration

- `codex` CLI **≥ 0.128.0** (Goals introduced in 0.128.0 — verify with
  `codex --version`; older pins like 0.122.0 must be upgraded).
- No MCP server. `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": ["Bash(codex --version)", "Bash(codex exec *)", "Bash(codex *)"]
  }
}
```

### Invocation pattern (goal-first, then session turns)

```bash
# Turn 0 — open the thread by setting the Goal (template from local/develop/v2/goals/)
codex exec --full-auto -m "gpt-5.4 xhigh" -C "$PWD" -o /tmp/codex-goal.md \
  "$(cat local/develop/v2/goals/phase-c.goal.md | sed 's/{SESSION}/C2/')"

# Turn 1..n — resume the SAME thread with the session prompt and follow-ups
codex exec resume --last -m "gpt-5.4 xhigh" \
  "$(awk '/^## Session C2/,/^## ✅ Session C2/' local/develop/v2/PhaseC_prompts.md)"
codex exec resume --last -m "gpt-5.4 xhigh" "Continue toward the goal."
```

- Goals are **thread-scoped state**: setting the goal in turn 0 and resuming the
  same thread keeps the contract attached to all the evidence (diffs, test runs).
  One session = one thread = one goal. Never reuse a thread across sessions.
- `--full-auto` ≡ workspace-write sandbox without approval prompts.
  Never use `--dangerously-bypass-approvals-and-sandbox`.
- `-o <file>` captures the final message for quality-checker verification.
- ⚠️ Verify once on your installed version that `codex exec` accepts a leading
  `/goal` message in non-interactive mode (it is documented for the composer).
  If it does not, fall back to: run `codex` interactively for turn 0 to set the
  goal, or inline the goal contract as a `[GOAL CONTRACT]` block at the top of
  every `codex exec` prompt — the six elements below matter more than the slash
  command itself.

### Goal lifecycle in our workflow

```
set (/goal, turn 0)
  → work (session prompt + continuation turns)
  → evidence check (Codex must run the verification commands itself)
  → STOP — Codex reports; quality-checker independently re-runs tox/ruff/mypy
  → human checklist from PhaseX_prompts.md → human commits
  → /goal clear (or simply end the thread)
```

Codex may mark the goal complete **only** when the verification surface is GREEN
in-thread. quality-checker re-verifies independently — Codex's claim is never
trusted without re-running the gate. Pause/resume/clear authority stays with us.

### Writing goals — the six required elements

Every goal must contain: **Outcome / Verification surface / Constraints /
Boundaries / Iteration policy / Blocked stop condition.** A goal missing the
blocked-stop condition is rejected — that clause is what stops Codex from
"fixing" a RED v1 test by editing it.

### Shared goal skeleton (all phases)

Stored at `local/develop/v2/goals/_skeleton.goal.md`; phase files below fill the
`{...}` slots:

```
/goal Complete rdetoolkit v2 Session {SESSION} exactly as specified in
local/develop/v2/Phase{P}_prompts.md (§Session {SESSION}), with Design.md as the
overriding spec. DONE means: {OUTCOME}, verified by {VERIFICATION} — all of:
`.venv/bin/tox -e py312-module` fully GREEN (v1+v2), `.venv/bin/tox -e py312-ruff`
and `.venv/bin/tox -e py312-mypy` clean, run in this thread with output shown.
Constraints that must hold at every step: never modify files under tests/ root;
types.py, errors.py, errors.pyi are append-only; never implement Trace/Compile/
pre-execution DAG machinery (ADR-020); never import rdetoolkit._core from v2
modules; do not git commit; {EXTRA_CONSTRAINTS}. Boundaries: create/edit only
{TARGET_FILES}; read anything. Iteration policy: strict TDD — write or run the
failing test first, confirm RED, make the smallest change, re-run, and after each
cycle state what changed and the next experiment. Blocked stop condition: if a
tests/-root (v1) test goes RED, if the session spec conflicts with Design.md, if
an append-only rule would have to be broken to proceed, or if the same failure
survives 3 distinct fix attempts — STOP immediately, do not work around it, and
report: attempted paths, evidence (test output), the exact blocker, and the
decision/input you need.
```

### Per-phase goal parameters (`local/develop/v2/goals/phase-{a..f}.goal.md`)

**Phase A — contracts & settlement**
- OUTCOME: error catalog unified to int codes with hierarchy (A1) / canonical
  reserved types `{paths,out,config,invoice,iteration}` and versioned Event-
  RunReport schemas (A2) / trace machinery deleted, B5 revert + B6 stub cleanup
  done (A3)
- VERIFICATION adds: `git diff HEAD -- src/rdetoolkit/errors.py(.pyi) | grep '^-'`
  empty; `python scripts/gen_error_docs.py --check`; A3: `git diff main -- tests/`
  empty, `core.pyi` absent, `_core.pyi` present
- EXTRA_CONSTRAINTS: A3 deletions limited to the explicit file list in the
  session prompt; `dag.rs` content untouched except the freeze header
- Note: **A3 is preferably NOT delegated** (Pipeline S). If delegated anyway, the
  goal's boundaries clause lists every deletable path explicitly.

**Phase B — runner skeleton & platform contracts**
- OUTCOME: lifecycle steps 1–6 ordered and tested; W1001 emitted on mode
  override; tile path resolution incl. `divided/`; `job.failed` written only by
  finalize in v1 format with catalog int codes
- VERIFICATION adds: `tox ... -- tests/v2/golden/ -v` GREEN — directory-tree
  parity with the v1 code path on ≥3 modes, where the expected tree is **generated
  by running v1**, never hand-written
- EXTRA_CONSTRAINTS: `domain/mode.py` priority order unchanged;
  `write_job_errorlog_file` called, not reimplemented

**Phase C — eager node/flow & provenance**
- OUTCOME: `@node`/`@flow` fully transparent plain functions; registry with
  E2001; provenance with per-call `call_id`, edge reconstruction with
  exact|heuristic confidence; flow-boundary DI with E2003/E2004; opt-in type
  check with zero cost when off
- VERIFICATION adds: `tests/v2/core/test_eager_semantics.py` GREEN (the legacy-B2
  regression suite: if/loop/f-string/literal/default-arg/container/repeat-call);
  determinism test GREEN; PBT with branching+merging shapes GREEN
- EXTRA_CONSTRAINTS: no DI inside `@node`; no `sys.setprofile`-style global hooks

**Phase D — iteration & end-to-end**
- OUTCOME: 5 mode iterators with correct tile semantics; error policy
  continue/fail_fast with success/partial/failed; RunAggregator independent of
  EventSink; `workflows.run` dispatch with v1 path byte-identical
- VERIFICATION adds: `tests/v2/e2e/ -v` GREEN on ≥3 modes (tree parity + report
  schema + job.failed artifact); `git diff` shows zero changes to v1 processing
  files other than the dispatch block in `workflows.py`
- EXTRA_CONSTRAINTS: no `Executor` class; no DeprecationWarning on the v1 path

**Phase E — CLI**
- OUTCOME: run/--validate-only, nodes list|describe|lint, flows, graph (3
  formats from provenance), report show, repro export→import→run round-trip,
  migrate check; exit codes 0/1/2/3 uniform
- VERIFICATION adds: `rdetoolkit --help` still lists init/gen-invoice/
  gen-excelinvoice/archive; parametrized exit-code test GREEN; v1 CLI tests GREEN
- EXTRA_CONSTRAINTS: typer; do not implement `plan`/`debug-node`; only
  `cli/main.py` registration may touch existing CLI files; graph rendering in
  pure Python (no `_core`)

**Phase F — builtin nodes, protocols, plugins, docs**
- OUTCOME: builtin node set registered & listed; canonical Protocols replace old
  ones (removals logged in CHANGELOG_v2.md); `as_node` proves v1 handler-class
  migration; plugin discovery with NO lifecycle hooks; migration guide + docs
  with executed examples; traceability.md covers every Design §14 row
- VERIFICATION adds: `mkdocs build --strict`; `gen_error_docs.py --check`;
  doctest/executed-example tests GREEN; `rdetoolkit nodes list` shows builtins
- EXTRA_CONSTRAINTS: builtin nodes get no framework privileges; v1
  rde2util/Meta read-only (port, don't modify)

### Goal anti-patterns (reject these)

- `/goal Implement Phase C` — no verification surface, no constraints.
- Any goal whose completion can be satisfied by **weakening a test** — the
  constraints clause must make tests/ root and acceptance tests immutable.
- One goal spanning multiple sessions or phases — thread evidence gets stale and
  budget accounting becomes meaningless.

### Codex Prompt Template (turn 1, after the goal is set)

```
[ROLE] You are implementing rdetoolkit v2 Session {SESSION} under the active Goal.

[CONTEXT]
- Python 3.12, strict mypy, ruff; test runner: .venv/bin/tox -e py312-module
- Canonical spec: local/develop/v2/Design.md (§ refs in the task)
- Rules: AGENTS.md (read in full; §8.2 Forbidden Actions especially)
- Execution model: eager + provenance. NO trace, NO compile, NO RustDAG.

[TASK]
<paste the Session block from PhaseX_prompts.md verbatim>

[REPORTING]
After each TDD cycle: what changed, test output tail, next step.
On completion: paste the verification command outputs required by the Goal.
On blocker: follow the Goal's blocked stop condition exactly.
```

### Delegation criteria

**Delegate to Codex (with goal):** all session implementation in Phases A1, A2,
B–F; large test-suite authoring; mechanical refactors.
**Keep in Claude:** Phase A3 settlement (deletion-heavy), architecture decisions,
Design.md edits, goal authoring/review, anything requiring judgment about
*whether* a spec is right rather than *how* to satisfy it.

### Choosing between subagent and Skill

- Parallel dispatch / long sessions → `codex-worker` subagent (isolates I/O).
- Single ad-hoc delegation → `/codex-delegate <task-file>` in main context.
Both use the same goal-first invocation pattern.

---

## Common Development Patterns

### v2 @node / @flow (eager)

```python
from rdetoolkit import node, flow

@node(tags=["io"], version="1.0.0")
def read_csv(paths: InputPaths) -> tuple[Metadata, pd.DataFrame]:
    """Read CSV from input paths."""
    ...

@flow
def xrd_pipeline(paths: InputPaths, out: OutputContext, config: RdeConfig) -> None:
    meta, df = read_csv(paths)
    if config.custom.get("normalize", True):   # plain Python — by design
        df = normalize(df, threshold=0.3)
    save_csv(df, out, "structured.csv")
    save_meta(meta, out)
```

### Protocol adapter / Result / Re-export

```python
read_xrd = as_node(RigakuReader(), method="read")
from rdetoolkit.result import Success, Failure, Result      # v1, use as-is
from rdetoolkit.utils.encoding import detect_encoding  # noqa: F401  (re-export)
```

### rdeconfig.yaml v2 sections (Design §4.4, §7.2, §3.2)

```yaml
policy:
  node_enforcement: off        # off (default) | recommend | strict
execution:
  type_check: off              # off (default) | warn | strict
  on_iteration_error: continue # fail_fast | continue (default)
plugin:
  preferred_handler:
    ".ras": "rdetoolkit_xrd.readers:RigakuReader"
# v1 sections preserved unchanged
system:
  extended_mode: null
  save_raw: true
  save_thumbnail_image: true
```

(Former `compile:` section is retired with the compile phase.)

---

## Dependencies

- **Core**: pandas, polars, pydantic, jsonschema, openpyxl, PyYAML, typer
- **v2 Python additions**: hypothesis (PBT)
- **Rust**: v1 crates only; `petgraph` remains in Cargo.toml for the frozen
  `dag.rs` but is not on any v2.0 path
- **Build**: maturin / **Dev**: pytest, ruff, mypy, tox, mkdocs, hypothesis

---

## Additional Resources

- Documentation: https://nims-mdpf.github.io/rdetoolkit/
- v2 Design: `local/develop/v2/Design.md` / Phase prompts: `Phase{A..F}_prompts.md`
- Goal templates: `local/develop/v2/goals/`
- Contributing Guide: `CONTRIBUTING.md`

---

## Local Rules

- Think in English, respond in Japanese.
- Never modify v1 test files (`tests/` root) — v2 tests go to `tests/v2/` only.
- Full `tox -e py312-module` GREEN is the gate for every session end and every
  phase merge — no exceptions.
- Never implement retired-design machinery (Trace/Compile/RustDAG-in-v2) even if
  asked by an outdated document; raise the conflict instead.
- One Codex thread = one session = one `/goal`. Goals must include all six
  elements; goals without a blocked-stop condition are rejected.
- The human commits. Agents stop and paste results.

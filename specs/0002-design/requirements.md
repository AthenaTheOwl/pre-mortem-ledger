# Spec 0002 — Design ledger

This is the design ledger for the v0.1 cut. It records every R-PML
requirement that lands in code in this spec, what changed since spec
0001, and which decisions are intentionally deferred.

## R-PML-101 — runnable CLI
`premortem new`, `premortem status`, `premortem render`, and
`premortem ledger {list,record}` are exposed as a console_script entry
point declared in `pyproject.toml`. Each verb exits zero on success.

## R-PML-102 — Pydantic mirror of JSON Schema
`src/premortem/schema.py` is the structural source of truth for the
Python side. Round-trip tests pin it to
`schemas/premortem.schema.json`. The JSON Schema remains the source of
truth for non-Python validators (jq, TypeScript readers, GitHub
content checks).

## R-PML-103 — append-only ledger
The control-plane framing requires an explicit ledger of scoring runs.
`data/ledger/runs.jsonl` is append-only JSONL;
`pre_mortem_ledger.ledger.append_ledger` refuses to overwrite a `run_id`
and refuses a second row with the same `(month, run_type)` pair. The
`2026-M06-initialization` row is the seed row shipped with v0.1.

## R-PML-104 — failure-mode rubric is closed-set
Every `rubric_category` referenced in a pre-mortem file must exist in
`rubric/failure_modes.yaml`. `scripts/validate_premortem_schema.py`
enforces this in addition to the JSON Schema. Adding a new category
requires editing the rubric first; this is the mechanism that keeps
the taxonomy from drifting.

## R-PML-105 — uv + dependency-groups
`pyproject.toml` declares dev dependencies under `[dependency-groups]`,
not `[project.optional-dependencies]`. `[tool.uv]` sets `package = true`
so the project itself is editable-installed into the venv on
`python -m uv sync`. Without these two blocks, `python -m uv run pytest`
falls back to system Python and `from pre_mortem_ledger import schema`
raises ModuleNotFoundError.

## R-PML-106 — methodology doc
`docs/METHODOLOGY.md` documents the monthly cadence, what counts as an
observability trigger, what the status enum means, how a run gets
recorded in the ledger, and what triggers a methodology revisit. Read
this before authoring the first real position file. A
backwards-compatible pointer copy lives at `docs/product-brief.md` /
`docs/system-map.md` so existing links keep working.

## R-PML-107 — system map
`SYSTEM_MAP.md` (root) enumerates the inputs, the outputs, the gates
between them, and the directories that hold each. It is the
single-page answer to "what does this repo touch?"

## R-PML-108 — product brief
`PRODUCT_BRIEF.md` (root) is the half-page answer to "what does this
repo decide?" — written for a reader who has not read AGENTS.md or any
spec. Frames the monthly loop as the recurring trim / hedge / hold
question.

## R-PML-109 — STATUS gate contract
`STATUS.md` carries three H2 sections with exactly these headings:
`## Current state`, `## Known limits`, `## Next feature queue`. The
contract gate matches the literal strings; renaming them silently
breaks the next factory run.

## R-PML-110 — out-of-scope guard maintained
Spec 0001's R-PML-010 still holds: no live market data, no broker
APIs, no order routing. The CLI verbs added in 0002 do not change
this surface.

## What this spec does not do

- No CI workflow. The gates run locally; CI is deferred to spec 0003.
- No Brier back-scoring. The `prior_run_brier` field is wired through
  the ledger row, but the calculation that fills it lands in spec
  0003 after the first real status_log entries exist.
- No integration with thesis-pillar-tracker. Pre-mortems still read
  from `config/positions.yaml`, not from a sibling repo.

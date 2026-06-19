# Spec 0001 — Foundation

## R-PML-001 — repo scaffold
Repo lives at `e:/claude_code/random-apps/pre-mortem-ledger`. MIT license;
copyright Vignesh Gopalakrishnan. AGENTS.md, README.md, LICENSE,
.gitignore present at the root.

## R-PML-002 — pre-mortem schema
`schemas/premortem.schema.json` defines the typed shape of a single
pre-mortem: `position`, `month` (YYYY-Mnn), `failure_modes[]` with
`title`, `narrative`, `observability_triggers[]`, `rank`, plus a
`status_log[]` that is appended to in subsequent months.

## R-PML-003 — position registry
`config/positions.yaml` lists registered positions with `ticker`,
`exposure_tier` (concentrated / sized / probe), and `since` date. The
monthly runner picks the largest currently-tagged `concentrated` row.

## R-PML-004 — failure-mode rubric
`rubric/failure_modes.yaml` enumerates recurring failure categories
(thesis-pillar invalidation, capital-allocation regime change,
operating-leverage reversal, sector-rotation, regulatory hit, etc.).
Each pre-mortem failure mode is tagged with one category.

## R-PML-005 — monthly file naming
Pre-mortems live at `premortem/<position>-<year>-M<nn>.md`. File name
must round-trip through the schema validator.

## R-PML-006 — status log append-only
Once a `status_log` entry exists for a given `(failure_mode_id, month)`
it is not edited; new months append new entries. The validator enforces
this.

## R-PML-007 — example pre-mortem
`examples/premortem-EXAMPLE-2026-M07.md` ships a worked example with
3 failure modes, observability triggers per mode, and an empty
status_log. The example uses a placeholder ticker `EXAMPLE` so no real
position is leaked.

## R-PML-008 — voice lint stub
`scripts/voice_lint.py` is copied from the portfolio voice spec and
runs against `premortem/*.md`. v0 stub only checks the banlist; the
structural anti-patterns ship in spec 0002.

## R-PML-009 — spec check
`scripts/spec_check.py` scans this file and confirms every
`R-PML-NNN` referenced in `design.md` and `tasks.md` exists in
`requirements.md`.

## R-PML-010 — out-of-scope guard
The repo refuses to ingest live market data, order books, or broker
APIs in v0. README and AGENTS.md state this explicitly.

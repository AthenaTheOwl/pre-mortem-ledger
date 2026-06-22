# Spec 0002 — Design

## Goal of this cut

Spec 0001 named the schema and the rubric. Spec 0002 lands the runnable
substrate: a Python package, a CLI, tests, the methodology doc, and the
first ledger row. After this spec lands, the monthly loop can begin for
real next month with a real ticker in `config/positions.yaml`.

## Package layout

```
src/pre_mortem_ledger/
  __init__.py      # public surface (R-PML-102)
  schema.py        # Pydantic + YAML front-matter I/O
  rubric.py        # load + closed-set check (R-PML-104)
  monthly.py       # position picker + scaffold writer (R-PML-101)
  ledger.py        # append-only ledger (R-PML-103)
  score.py         # Brier scoring helpers (deferred wiring in R-PML-103)
  report.py        # INDEX.md and ledger-report renderers
  cli.py           # argparse entry point (R-PML-101)
```

The CLI is `argparse`, not click. The verb surface is small enough that
the third-party dep is not worth the install footprint.

## Why a separate ledger directory

The pre-mortems in `premortem/` are the artifacts of each monthly run.
The ledger row in `data/ledger/runs.jsonl` is the meta-record of *when*
that run happened, *what* it covered, and (after spec 0003) *how* well
last month's predictions held up. Keeping the two surfaces apart means
the pre-mortems remain pure write-ups; the calibration accounting lives
in its own append-only log (R-PML-103). The `data/` prefix keeps the
calibration substrate visually distinct from the position artifacts.

## Filename convention

`premortem/<position>-<year>-M<nn>.md`. Enforced by
`PreMortem.expected_filename()` and by
`scripts/validate_premortem_schema.py`. The `M<nn>` form (not `MM`) is
deliberate: it disambiguates from quarter or week numbering in adjacent
projects.

## Validation pipeline

A pre-mortem file is valid when:

1. The YAML front-matter parses and matches the Pydantic model
   (R-PML-102).
2. The same payload validates against
   `schemas/premortem.schema.json` (R-PML-102).
3. Every `rubric_category` referenced exists in
   `rubric/failure_modes.yaml` (R-PML-104).
4. The filename matches `pm.expected_filename()`.

`scripts/validate_premortem_schema.py` runs all four in one pass and
prints one line per failure.

## uv packaging

R-PML-105 documents the trap. `[dependency-groups]` + `[tool.uv]
package = true` is the supported combination as of uv 0.4+. Treating
the dev deps as `optional-dependencies` (the pre-uv habit) silently
breaks the venv.

## Status enum semantics

| status | meaning |
|---|---|
| `unchanged` | The observability trigger has not fired this month. |
| `evidence-emerging` | Partial evidence aligned with the trigger; not conclusive. |
| `observed` | The trigger fired. The failure mode is no longer hypothetical. |
| `retired` | Context changed enough that the mode no longer applies. |

`observed` is the status the user is watching for: it is the recurring
decision signal — trim, hedge, or hold.

## Out of scope

- Brier scoring (deferred to spec 0003 once the first month of
  `status_log` entries exists).
- Embedding-based auto-tagging of failure modes against the rubric.
- Cross-repo evidence ingestion (e.g. from a Thesis Pillar Tracker
  sibling).

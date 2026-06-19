# Spec 0001 — Design

## Shape

One CLI, one schema, one Markdown directory. The repo is small on
purpose. The discipline lives in the rubric and the monthly cadence,
not in code complexity.

```
config/positions.yaml      # registered positions (R-PML-003)
rubric/failure_modes.yaml  # taxonomy (R-PML-004)
schemas/premortem.schema.json  # typed shape (R-PML-002)
src/premortem/
  cli.py                   # new / status / render
  schema.py                # Pydantic mirror of the JSON schema
  rubric.py                # load + lookup
  monthly.py               # picks the position, scaffolds the file
premortem/                 # one Markdown file per (position, month)
examples/                  # worked example with placeholder ticker
scripts/
  voice_lint.py            # portfolio voice spec (R-PML-008)
  spec_check.py            # requirements traceability (R-PML-009)
tests/
  test_schema.py
  test_monthly.py
  test_status_append_only.py
```

## Data flow

1. User edits `config/positions.yaml` with current exposure tiers.
2. `uv run premortem new --month 2026-Mnn` reads positions, picks the
   largest `concentrated` row, scaffolds `premortem/<ticker>-2026-Mnn.md`
   with empty failure-mode templates.
3. User writes the 3-5 failure modes by hand. The schema validator
   refuses to render a pre-mortem with fewer than 3 modes or missing
   observability triggers.
4. `uv run premortem status --month 2026-Mnn` reopens every prior open
   pre-mortem and appends a new `status_log` entry (one of: unchanged,
   evidence-emerging, observed, retired).
5. `uv run premortem render --month 2026-Mnn` produces a single
   index page `premortem/INDEX.md` summarizing the month.

## Why Markdown plus YAML

Same reason as the rest of the portfolio: Git-diffable, human-readable,
agent-readable. No database. The schema lives in JSON Schema so
non-Python readers (TypeScript, jq) can validate the same files.

## Status log shape

Each failure mode owns its own append-only `status_log[]`. An entry is
`{month, status, evidence_ref, note}`. `status` is one of:

- `unchanged` — observability trigger has not fired.
- `evidence-emerging` — partial evidence aligned with the trigger.
- `observed` — trigger fired; failure mode is no longer hypothetical.
- `retired` — context changed enough that the mode no longer applies.

`observed` is the status that signals the recurring decision: trim,
hedge, or hold.

## What is not in spec 0001

- Brier-style back-scoring of resolved pre-mortems (spec 0003).
- Auto-tagging of failure modes against the rubric via embeddings
  (spec 0004).
- Integration with thesis-pillar-tracker as an upstream evidence
  source (spec 0005).

Spec 0002 lands the rendering + voice_lint structural checks + the
first real position file.

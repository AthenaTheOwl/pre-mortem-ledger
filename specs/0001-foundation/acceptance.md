# Spec 0001 — Acceptance

v0 is done when the following hold.

## Repo shape

- README.md, LICENSE, AGENTS.md, .gitignore at the root.
- `specs/0001-foundation/` contains requirements / design / tasks /
  acceptance.
- `docs/first-pr.md` describes the literal next PR.

## Commands

After PR 1-3 land:

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_premortem_schema.py examples/premortem-EXAMPLE-2026-M07.md
```

All four exit zero.

## Functional gates

- `examples/premortem-EXAMPLE-2026-M07.md` validates against the
  schema and contains exactly 3 failure modes, each with at least one
  observability trigger.
- `uv run premortem new --month 2026-M07 --position EXAMPLE` writes
  a new file that round-trips through the schema validator.
- `uv run premortem status --month 2026-M08` against the example
  appends a new `status_log` entry without mutating prior entries.
- `scripts/spec_check.py` confirms every `R-PML-NNN` referenced in
  `design.md` and `tasks.md` exists in `requirements.md`.

## Out of scope for v0 acceptance

- Brier back-scoring.
- Real position data.
- CI workflow.
- Integration with thesis-pillar-tracker.

Those land in later specs.

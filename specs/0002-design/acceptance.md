# Spec 0002 — Acceptance

v0.1 is done when every check below passes.

## Repo shape

- `src/pre_mortem_ledger/{schema,rubric,monthly,ledger,score,report,cli}.py`
  all exist.
- `schemas/premortem.schema.json`, `config/positions.yaml`,
  `rubric/failure_modes.yaml` all exist.
- `examples/premortem-EXAMPLE-2026-M07.md` exists and round-trips
  through the schema.
- `data/ledger/runs.jsonl` contains exactly one row with
  `run_id = "2026-M06-initialization"`.
- `STATUS.md` has the three required H2 sections (R-PML-109).
- `PRODUCT_BRIEF.md` and `SYSTEM_MAP.md` exist at the repo root
  (R-PML-107, R-PML-108).
- `docs/METHODOLOGY.md` exists with a `## What revisits this` section
  (R-PML-106).
- `decisions/DEC-0001-v0.1-cut.md` records the v0.1 design decisions.

## Commands

These exit zero (locally, after `python -m uv sync`):

```bash
python -m uv run pytest -q
python -m uv run python scripts/voice_lint.py
python -m uv run python scripts/spec_check.py
python -m uv run python scripts/validate_premortem_schema.py examples/premortem-EXAMPLE-2026-M07.md
```

## Functional gates

- `python -m uv run premortem new --month 2026-M08 --position EXAMPLE`
  writes a file that round-trips through the schema validator.
- `python -m uv run premortem status --file <path> --month 2026-M09
  --id fm-1 --set observed` appends a new `status_log` entry without
  mutating prior entries.
- `python -m uv run premortem ledger record --month 2026-M07 --type
  monthly --positions EXAMPLE --modes 3` appends a row to
  `data/ledger/runs.jsonl`. A second invocation with the same
  `(month, type)` pair errors.

## Out of scope for v0.1 acceptance

- Real position data in `config/positions.yaml`.
- Brier back-scoring.
- CI workflow.
- Structural voice_lint rules.

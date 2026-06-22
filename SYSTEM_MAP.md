# System map

Single-page answer to "what does this repo touch?"

## Inputs

| Path | Format | Owned by |
|---|---|---|
| `config/positions.yaml` | YAML | user |
| `rubric/failure_modes.yaml` | YAML | rubric-keeper |
| User's investing notes | freeform | user (out-of-tree) |

## Outputs

| Path | Format | Producer |
|---|---|---|
| `premortem/premortem-<TICKER>-<YYYY>-M<nn>.md` | YAML front-matter + Markdown body | `premortem new`, then user |
| `premortem/INDEX.md` | Markdown | `premortem render` |
| `data/ledger/runs.jsonl` | JSONL, append-only | `premortem ledger record` |
| `data/ledger/<YYYY>-M<nn>.md` | Markdown | user (optional companion) |

## Gates

Run locally; CI lands in spec 0003.

| Gate | Command | What it checks |
|---|---|---|
| Tests | `python -m uv run pytest -q` | schema, CLI, ledger append-only |
| Voice | `python -m uv run python scripts/voice_lint.py` | banlist (structural rules: spec 0003) |
| Spec ref | `python -m uv run python scripts/spec_check.py` | every `R-PML-NNN` referenced in design/tasks/acceptance is declared in requirements |
| Schema | `python -m uv run python scripts/validate_premortem_schema.py <path>` | JSON Schema + rubric closed-set + filename |

## Internal modules

```
pre_mortem_ledger/
  __init__.py       public surface
  schema.py         Pydantic + YAML front-matter I/O
  rubric.py         load + closed-set check
  monthly.py        position picker + scaffold writer
  ledger.py         append-only ledger reader/writer
  score.py          Brier scoring helpers (wired into ledger in spec 0003)
  report.py         INDEX.md and ledger-report renderers
  cli.py            argparse entry point
```

## External dependencies

- `pydantic >= 2.6` — schema validation.
- `pyyaml >= 6.0` — YAML I/O for positions, rubric, and pre-mortem
  front-matter.
- `jsonschema >= 4.21` — JSON Schema validation in
  `scripts/validate_premortem_schema.py` and the schema round-trip
  test.
- `pytest`, `pytest-cov`, `ruff` — dev-only; declared under
  `[dependency-groups]` so `python -m uv sync` picks them up.

## Out of scope

- Live market data, broker APIs, order routing. (R-PML-110)
- Multi-user portfolios.
- Quantitative factor models. The failure modes are written-out
  hypotheses, not regression coefficients.

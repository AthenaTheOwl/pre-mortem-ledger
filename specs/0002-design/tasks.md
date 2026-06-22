# Spec 0002 — Tasks

These are the units of work that landed in v0.1. The checked rows are
the ones that ship with this cut.

## v0.1 cut (this PR)

- [x] Write `src/pre_mortem_ledger/schema.py` (R-PML-102).
- [x] Write `src/pre_mortem_ledger/rubric.py` with closed-set check
      (R-PML-104).
- [x] Write `src/pre_mortem_ledger/monthly.py` with `pick_target` +
      scaffold (R-PML-101).
- [x] Write `src/pre_mortem_ledger/ledger.py` with append-only
      enforcement (R-PML-103).
- [x] Write `src/pre_mortem_ledger/score.py` Brier helpers (R-PML-103
      back-scoring wiring deferred to spec 0003).
- [x] Write `src/pre_mortem_ledger/report.py` INDEX.md and ledger-report
      renderers.
- [x] Write `src/pre_mortem_ledger/cli.py` with `new / status / render /
      ledger` (R-PML-101).
- [x] Write `pyproject.toml` with `[dependency-groups]` + `[tool.uv]`
      (R-PML-105).
- [x] Write `schemas/premortem.schema.json` (R-PML-102).
- [x] Write `config/positions.yaml` placeholder row.
- [x] Write `rubric/failure_modes.yaml` with at least 8 categories
      (R-PML-104).
- [x] Write `examples/premortem-EXAMPLE-2026-M07.md` worked example.
- [x] Write `tests/` covering schema, monthly, status-log, CLI, rubric.
- [x] Write `scripts/voice_lint.py` (banlist only — R-PML-110 carries
      forward).
- [x] Write `scripts/spec_check.py` (R-PML-109 reference checker
      reused for 0002).
- [x] Write `scripts/validate_premortem_schema.py` (R-PML-104).
- [x] Write `STATUS.md` with the three required H2 sections
      (R-PML-109).
- [x] Write `PRODUCT_BRIEF.md` at the repo root (R-PML-108).
- [x] Write `SYSTEM_MAP.md` at the repo root (R-PML-107).
- [x] Write `docs/METHODOLOGY.md` with the "What revisits this" section
      (R-PML-106).
- [x] Write `decisions/DEC-0001-v0.1-cut.md` recording this cut.
- [x] Seed `data/ledger/runs.jsonl` with the `2026-M06-initialization`
      row (R-PML-103).

## Deferred to spec 0003

- [ ] CI workflow that runs the four gate scripts on every push.
- [ ] Brier back-scoring pass that fills `prior_run_brier` after the
      second monthly run.
- [ ] Structural anti-pattern checks in `voice_lint.py` (reversal
      shape, marketing scaffolds).
- [ ] First real ticker in `config/positions.yaml`.

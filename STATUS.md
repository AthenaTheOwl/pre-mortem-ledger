# Status — Pre-Mortem Ledger

Cut: v0.1, recorded 2026-06-22.

## Current state

- Python package `pre_mortem_ledger` is installable. `pyproject.toml`
  declares dev deps under `[dependency-groups]` and pins
  `[tool.uv] package = true`.
- CLI verbs `new`, `status`, `render`, and `ledger {list,record}` all
  exit zero on the happy path. Argparse-only; no third-party CLI dep.
  The console-script name `premortem` is unchanged.
- JSON Schema in `schemas/premortem.schema.json` is the structural
  source of truth. Pydantic mirror in `pre_mortem_ledger/schema.py`
  is pinned to it by a round-trip test.
- Rubric in `rubric/failure_modes.yaml` lists 10 failure categories.
  `scripts/validate_premortem_schema.py` enforces that every
  `rubric_category` referenced in a pre-mortem exists in the rubric.
- Worked example `examples/premortem-EXAMPLE-2026-M07.md` passes the
  schema validator, the rubric check, and the filename convention.
- First ledger row is checked in:
  `data/ledger/runs.jsonl` contains the `2026-M06-initialization` row
  with `prior_run_brier = null`.
- Brier scoring helpers ship in `pre_mortem_ledger/score.py` and
  index/ledger renderers ship in `pre_mortem_ledger/report.py`.
- Tests cover schema round-trip, append-only status_log, monthly
  scaffolding, rubric closed-set, the CLI verbs, and the shipped
  ledger row. `python -m uv run pytest -q` is the gate.
- Root-level `PRODUCT_BRIEF.md` and `SYSTEM_MAP.md` are the half-page
  answers to "what does this decide?" and "what does this touch?".
- `docs/METHODOLOGY.md` documents how to author a useful pre-mortem
  and enumerates what triggers a methodology revisit.
- `decisions/DEC-0001-v0.1-cut.md` records the design decisions behind
  this cut.

## Known limits

- `prior_run_brier` is null. The Brier back-scoring pass that fills it
  lands in spec 0003, after the first real `status_log` entries from
  the 2026-M07 → 2026-M08 transition exist.
- `voice_lint.py` checks the banlist only. The structural anti-pattern
  checks (the "X isn't Y; Z is the W" reversal shape, marketing
  scaffolds, em-dash overuse) are deferred to spec 0003.
- `config/positions.yaml` still names only the `EXAMPLE` placeholder.
  No real position has been registered. The next monthly run is the
  first one that touches the real book.
- No CI workflow. The four gate scripts (`pytest`, `voice_lint`,
  `spec_check`, `validate_premortem_schema`) run locally only.
- No cross-repo evidence ingestion. Triggers fire on user-supplied
  evidence references in `status_log` entries, not on signals pulled
  from a Thesis Pillar Tracker sibling.

## Next feature queue

- Wire CI: a GitHub Actions workflow that runs `pytest`, `voice_lint`,
  `spec_check`, and `validate_premortem_schema` on every push.
- Brier back-scoring: spec 0003 pass that compares the previous month's
  `status_log` entries against realized outcomes and writes a
  `prior_run_brier` into the next monthly ledger row.
- Structural voice rules: add the reversal-shape detector and a
  per-paragraph em-dash budget to `voice_lint.py`.
- Replace `EXAMPLE` with the first real concentrated position in
  `config/positions.yaml`, then run `premortem new --month 2026-M07`
  on the real book and `ledger record --type monthly` to record it.
- Add `premortem ledger score --month <m>` that computes the Brier
  delta in one command instead of requiring the caller to pass
  `--brier`.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing data/ledger/*.jsonl
- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: pyproject warnings - dev under optional-deps -- move to dependency-groups
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'pre_mortem_ledger/cli.py' is missing
- Resolve factory defect: expected file 'pre_mortem_ledger/score.py' is missing
- Resolve factory defect: expected file 'pre_mortem_ledger/ledger.py' is missing
- Resolve factory defect: expected glob 'data/ledger/*.jsonl' matched no files
- Resolve factory defect: expected glob 'decisions/DEC-*.md' matched no files
- Resolve factory defect: module 'cli' declares source 'pre_mortem_ledger/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'pre_mortem_ledger/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'pre_mortem_ledger/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'pre_mortem_ledger/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
- Resolve factory defect: pyproject warnings - dev under optional-deps -- move to dependency-groups
- Resolve factory defect: expected file 'pre_mortem_ledger/cli.py' is missing
- Resolve factory defect: expected file 'pre_mortem_ledger/score.py' is missing
- Resolve factory defect: expected file 'pre_mortem_ledger/ledger.py' is missing
- Resolve factory defect: module 'cli' declares source 'pre_mortem_ledger/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'pre_mortem_ledger/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'pre_mortem_ledger/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'pre_mortem_ledger/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log

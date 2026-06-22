# Pre-Mortem Ledger

Monthly forced pre-mortem on the largest active investing position. For each
position the ledger asks one question: if this is down 40% in 12 months, what
is the most likely written-out reason? The answers become falsifiable claims
tracked month-by-month against subsequent evidence.

## What this is

Generic investing tools do post-mortems after the fact. This repo runs the
opposite loop. Once a month, the largest position by exposure gets a
pre-mortem write-up with 3-5 named failure modes. Each failure mode carries
an observability trigger: a specific piece of evidence that, if observed,
would mean the failure mode is moving from imagined to real. The next month
the ledger revisits every open failure mode and updates its status.

The repo answers one recurring decision: has any pre-mortem reason become
observable enough this month to act on — trim, hedge, or hold?

Inputs: position list, prior pre-mortems, and the user's investing notes.
Outputs: `premortem/<position>-<year>-Mnn.md` with ranked failure modes,
observability triggers, and the rolling status of each prior month's claims.

## Status

v0.1. Runnable CLI, schema, rubric, and the first ledger row are checked
in. The `EXAMPLE` placeholder position is the only ticker registered;
`config/positions.yaml` acquires the first real ticker in the next
monthly run. See `STATUS.md` for the full state, known limits, and the
next-feature queue.

## How to run

```bash
python -m uv sync
python -m uv run premortem new --month 2026-M07
python -m uv run premortem status --file <path> --month 2026-M08 --id fm-1 --set unchanged
python -m uv run premortem render --month 2026-M07
python -m uv run premortem ledger record --month 2026-M07 --type monthly --positions EXAMPLE --modes 3
python -m uv run premortem ledger list
```

The four gate scripts run locally:

```bash
python -m uv run pytest -q
python -m uv run python scripts/voice_lint.py
python -m uv run python scripts/spec_check.py
python -m uv run python scripts/validate_premortem_schema.py examples/premortem-EXAMPLE-2026-M07.md
```

## Layout

```
.
├── AGENTS.md
├── LICENSE
├── PRODUCT_BRIEF.md         # half-page answer to "what does this repo decide?"
├── README.md
├── STATUS.md                # current state / known limits / next feature queue
├── SYSTEM_MAP.md            # inputs, outputs, gates, modules
├── config/
│   └── positions.yaml
├── data/
│   └── ledger/
│       ├── runs.jsonl       # append-only ledger of scoring runs
│       ├── 2026-M06.md      # human companion for the seed row
│       └── README.md
├── decisions/
│   └── DEC-0001-v0.1-cut.md
├── docs/
│   ├── METHODOLOGY.md
│   ├── first-pr.md
│   ├── product-brief.md
│   └── system-map.md
├── examples/
│   └── premortem-EXAMPLE-2026-M07.md
├── rubric/
│   └── failure_modes.yaml
├── schemas/
│   └── premortem.schema.json
├── scripts/
│   ├── spec_check.py
│   ├── validate_premortem_schema.py
│   └── voice_lint.py
├── specs/
│   ├── 0001-foundation/
│   └── 0002-design/
├── pre_mortem_ledger/
│   ├── __init__.py
│   ├── cli.py
│   ├── ledger.py
│   ├── monthly.py
│   ├── report.py
│   ├── rubric.py
│   ├── schema.py
│   └── score.py
└── tests/
```

## Why this exists

The user keeps a small, concentrated investing book. The portfolio already
has a Thesis Pillar Tracker and an Earnings Call Pillar Diff. The missing
loop is the forced pre-mortem: a structured exercise that names the
failure paths before they show up in price action. Resolved positions feed
back into the rubric so the failure-mode taxonomy sharpens with each
cycle.

## License

MIT. See `LICENSE`.

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

v0 scaffold. No code, no ingestion, no rendered pre-mortems. Spec 0001
defines the schema, the monthly run shape, and the gates that will land in
spec 0002. Nothing here is wired to a real position yet.

## How to run

Placeholder. The CLI lands in spec 0002. The intended shape:

```bash
uv run premortem new --position <ticker> --month 2026-07
uv run premortem status --month 2026-07
uv run premortem render --month 2026-07
```

For now, read `specs/0001-foundation/` to see the planned schema and the
first PR that follows this scaffold.

## Layout

```
.
├── AGENTS.md
├── LICENSE
├── README.md
├── docs/
│   └── first-pr.md
└── specs/
    └── 0001-foundation/
        ├── acceptance.md
        ├── design.md
        ├── requirements.md
        └── tasks.md
```

Future directories named in the spec:

- `premortem/` — one Markdown file per (position, month).
- `src/premortem/` — schema, CLI, rubric, status updater.
- `config/positions.yaml` — registered positions + exposure tiers.
- `rubric/failure_modes.yaml` — taxonomy of recurring failure categories.
- `tests/` — schema validation + rubric tests.

## Why this exists

The user keeps a small, concentrated investing book. The portfolio already
has a Thesis Pillar Tracker and an Earnings Call Pillar Diff. The missing
loop is the forced pre-mortem: a structured exercise that names the
failure paths before they show up in price action. Resolved positions feed
back into the rubric so the failure-mode taxonomy sharpens with each
cycle.

## License

MIT. See `LICENSE`.

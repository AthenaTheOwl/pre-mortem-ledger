# Product brief — Pre-Mortem Ledger

## What this decides

Once a month, the largest active investing position in the book gets a
forced pre-mortem. Three to five named failure modes are written out,
each with a concrete observability trigger. The next month, every prior
failure mode is re-scored against new evidence. The repo answers one
recurring question:

> Has any pre-mortem trigger fired this month? If yes — trim, hedge, or hold?

## Who this is for

The single-user investor running a concentrated book. Adjacent to the
Thesis Pillar Tracker (which watches what is supposed to be true) and
the Earnings Call Pillar Diff (which watches what management says).
Pre-Mortem Ledger watches the imagined failure paths that haven't shown
up in price action yet.

## What it is not

- Not a market-data feed. Inputs are the user's positions file and the
  user's notes.
- Not an alerting system. Triggers are evaluated by the user on the
  monthly cadence, not by a daemon.
- Not a portfolio-construction tool. The output is one Markdown file
  per (position, month), plus a ledger row.

## The monthly loop

1. Run `premortem new --month YYYY-Mnn`. The CLI reads
   `config/positions.yaml`, picks the longest-held concentrated row,
   and scaffolds a pre-mortem file with three blank failure-mode slots.
2. Fill in each slot: title, narrative, rank, rubric category, at
   least one observability trigger.
3. Run `premortem render --month YYYY-Mnn` to produce an
   `INDEX.md` for the month.
4. Record the run in the ledger:
   `premortem ledger record --month YYYY-Mnn --type monthly`.
5. Next month: `premortem status --file <path> --month <next> --id fm-N
   --set <status>` for every open failure mode.

## Why a ledger row per run

The ledger row is the meta-record of *when* the monthly exercise
happened and *how well* last month's predictions held up. It is the
control-plane substrate that lets a later spec compute a calibration
score (Brier delta) without re-reading every pre-mortem file. Rows are
append-only.

## Output shape

```
premortem/
  premortem-<TICKER>-<YYYY>-M<nn>.md    # one per (position, month)
  INDEX.md                              # rendered by `premortem render`

data/ledger/
  runs.jsonl                            # one row per run, append-only
  <YYYY>-M<nn>.md                       # optional human companion
```

# pre-mortem-ledger

Once a month, the largest position in the book gets asked a single rude question: if you're down 40% a year from now, what's the written-out reason? The answer isn't a feeling. It's three to five named failure modes, each with a piece of evidence that would tell you it stopped being imaginary.

## What it does

A post-mortem arrives after the loss, when the only thing left to do is name it. This runs the loop in the other direction. The biggest position by exposure gets a forced pre-mortem before anything goes wrong: 3-5 ranked failure modes, each one carrying an observability trigger — a specific thing you could watch for that would mean the failure has started to move from imagined to real.

Then the ledger keeps the receipts. Next month it revisits every open failure mode and re-scores it against what actually happened. The recurring decision it serves is narrow: did any of last month's reasons become observable enough to act on — trim, hedge, or hold? Inputs are a position list, the prior pre-mortems, and your own notes. Outputs are `premortem/<position>-<year>-Mnn.md` with the ranked modes, their triggers, and the rolling status of every claim you've made so far. Resolved positions feed back into the rubric, so the failure-mode taxonomy gets sharper each cycle instead of staying a blank form.

## Try it

```bash
python -m uv run premortem show
```

```
pre-mortem -- EXAMPLE (concentrated), 2026-M07
source: premortem-EXAMPLE-2026-M07.md

3 failure modes, ranked by current read of likelihood:

rank  failure mode                                          rubric category             status
----------------------------------------------------------------------------------------------
fm-1  Top customer renegotiates contract terms downward     customer-concentration      not yet re-scored
fm-2  Capital allocation pivots from buybacks to opport...  capital-allocation-regime   not yet re-scored
fm-3  Operating leverage reverses on flat revenue           operating-leverage-reve...  not yet re-scored

top trigger to watch (fm-1):
  - The customer's next earnings call names this vendor in a "vendor consolidation" or "cost discipline" section.
  - A new framework contract is filed with materially shorter duration than the prior one.

ledger:
  2026-M06  initialization  positions=EXAMPLE  modes=3  brier=n/a

headline: top failure mode for EXAMPLE is fm-1: Top customer renegotiates contract terms downward. nothing re-scored yet across 1 ledger run(s) -- all modes still imagined, not observed.
```

Ranked by current read of likelihood, worst first. Every mode reads "not yet re-scored" because the ledger has exactly one run on it — the imagined column is full and the observed column is empty, which is the honest state of a pre-mortem on day one.

## Live demo

The same committed pre-mortem and run ledger ship two ways. The CLI verb above is one. The other is a Streamlit page (`streamlit_app.py`) reading the same artifacts: pick a failure mode, read its narrative and its observability triggers, watch the run ledger fill in.

```bash
python -m uv run --with streamlit streamlit run streamlit_app.py
```

Deploy on Streamlit Cloud: repo `AthenaTheOwl/pre-mortem-ledger`, branch `main`, main file `streamlit_app.py`.

<!-- live-url: (add the deployed Streamlit Cloud URL here) -->

## How it connects

The book it watches over is small and concentrated, and two siblings already track the upside:

- [thesis-pillar-tracker](https://github.com/AthenaTheOwl/thesis-pillar-tracker) — the standing case for why each position is held.
- [earnings-pillar-diff](https://github.com/AthenaTheOwl/earnings-pillar-diff) — what each earnings call did to that case.

This is the missing third loop: the one that names the failure paths out loud before they show up in the price.

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

v0.1. The CLI, schema, rubric, and the first ledger row are checked in. `EXAMPLE` is the only ticker registered; `config/positions.yaml` gets its first real one on the next monthly run. `STATUS.md` has the full state, the known limits, and the next-feature queue.

## Layout

```
pre_mortem_ledger/        package: cli, ledger, monthly, report, rubric, schema, score
config/positions.yaml     the registered tickers (EXAMPLE for now)
rubric/failure_modes.yaml the failure-mode taxonomy that sharpens each cycle
schemas/premortem.schema.json
examples/                 the committed seed pre-mortem
data/ledger/              append-only runs.jsonl + the M06 companion row
scripts/                  the four local gates
specs/  decisions/  docs/  tests/
streamlit_app.py          browsable card view of the committed pre-mortem
```

## License

MIT. See `LICENSE`.

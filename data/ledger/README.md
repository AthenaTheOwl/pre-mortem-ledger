# `data/ledger/`

Append-only record of monthly scoring / calibration runs. One row per
run. Two formats kept in lockstep:

- `runs.jsonl` — one JSON object per line. Programmatic source of truth.
- `<month>.md` — human-readable companion for the row. Optional but
  encouraged for runs that record narrative decisions.

## Schema

Each row in `runs.jsonl` carries:

| field | type | meaning |
|---|---|---|
| `run_id` | string | `<month>-<run_type>`, unique. |
| `month` | string | `YYYY-Mnn`. |
| `run_type` | enum | `initialization` / `monthly` / `calibration`. |
| `positions_scored` | list | Tickers covered by this run. |
| `failure_modes_logged` | int | Total failure modes across all files. |
| `prior_run_brier` | number/null | Brier score of last month's predictions vs realized status. Null on the first run. |
| `notes` | string | Free text. |
| `schema_version` | int | Pinned to `1` in v0.1. |
| `extras` | object | Run-type-specific fields. |

## Append-only

`pre_mortem_ledger.ledger.append_ledger` refuses to write a row whose
`run_id` already exists, and refuses a second row with the same
`(month, run_type)` pair. Do not edit existing rows by hand. If a row is
wrong, append a `calibration` row that corrects it.

# Methodology

How to author a useful pre-mortem and how to think about each field.

## Cadence

One monthly run, executed in the first week of the calendar month. The
position chosen is the largest concentrated row in
`config/positions.yaml` by exposure tier then by `since` date (longest
held wins).

## Imagined horizon

The exercise asks: imagine it is twelve months from now and the
position is down forty percent. What is the most likely written-out
reason? The forty-percent figure is the anchor — large enough to force
a real failure mode, small enough to stay credible against a
concentrated single-name position.

## Writing one failure mode

Each failure mode carries six fields:

| Field | Constraint | Authoring note |
|---|---|---|
| `id` | `fm-N` | Stable identifier; never reused after retirement. |
| `title` | 4+ chars | One concrete event, not an abstraction. "Top customer cuts contract length" beats "execution risk". |
| `narrative` | 20+ chars | Two or three sentences. Explain the mechanism, not the conclusion. |
| `rank` | 1..N contiguous | Most likely is 1. Force a strict ranking — ties are a sign the failure modes overlap. |
| `rubric_category` | Must exist in rubric | One per failure mode. If the rubric does not name the right category, edit the rubric before the pre-mortem. |
| `observability_triggers` | 1+ entries | The signal that, if seen, means this hypothesis is no longer hypothetical. |

## Writing a useful trigger

A good observability trigger names a specific, datable artifact:

- "The next 10-Q shows operating cash flow below the prior four-quarter
  average by more than 25 percent."
- "An 8-K is filed announcing a CFO departure within 90 days."
- "Two consecutive monthly reseller surveys show net-new wins below
  the prior six-month average."

A bad trigger names a vibe:

- ~~"Sentiment turns negative."~~
- ~~"The thesis breaks down."~~
- ~~"Macro headwinds hit the sector."~~

The test: can two different readers agree on whether the trigger has
fired? If no, rewrite it.

## Status enum

Each `status_log` entry uses one of four statuses:

| status | meaning | What you do |
|---|---|---|
| `unchanged` | The trigger has not fired. | Nothing. Carry the failure mode into next month. |
| `evidence-emerging` | Partial evidence aligned with the trigger. | Note the evidence reference. Watch closely next month. |
| `observed` | The trigger fired. The failure mode is no longer hypothetical. | This is the decision signal — trim, hedge, or hold. |
| `retired` | Context changed enough that the mode no longer applies. | Note why in `note`. The failure mode is closed; do not re-score it. |

## The ledger row

Each monthly run also writes one row to `data/ledger/runs.jsonl`:

```json
{"run_id": "<month>-<run_type>", "month": "...", "run_type": "monthly",
 "positions_scored": ["..."], "failure_modes_logged": N,
 "prior_run_brier": null, "notes": "...", "schema_version": 1,
 "extras": {}}
```

`run_type` is one of:

- `initialization` — the very first run for a new install. No prior
  data to score against.
- `monthly` — the recurring run.
- `calibration` — a corrective entry that re-scores or annotates a
  prior row. Used when a `monthly` row was wrong and needs an
  override; the original row stays.

`prior_run_brier` is null in v0.1. Spec 0003 fills it from the
previous month's `status_log` entries.

## Failure-mode rubric

The rubric in `rubric/failure_modes.yaml` is a closed set. New
categories are added by editing the rubric first; the validator
refuses any pre-mortem that tags a category not in the rubric. After
a position is resolved, the rubric is revisited and tightened based
on what actually happened.

## What revisits this

The methodology is not write-once. Each of the following triggers a
re-read of this document and, where needed, an edit. Edits land
through a `calibration` ledger row and a paragraph in the next
`STATUS.md` "Known limits" section so the change is auditable.

- **A failure mode resolves.** When a position closes (sold, hedged,
  thesis invalidated), revisit the `status_log` and confirm the
  status enum semantics matched what actually happened. Tighten the
  description in this doc if the meaning drifted in practice.
- **A `retired` status is used.** "Retired" is the escape hatch and is
  the most likely place the methodology will be abused. Each use is
  reviewed at quarter end; if the same justification keeps surfacing,
  the rubric or the trigger-writing guidance is wrong.
- **A new rubric category is added.** Adding a category implies the
  prior taxonomy missed a class of failure. Revisit the rubric
  guidance section and the worked example to make sure the new
  category is illustrated.
- **The first non-null `prior_run_brier` posts.** Once spec 0003 lands
  and the first calibration delta exists, revisit the rank-to-prior
  schedule in `pre_mortem_ledger.score` and the status-to-outcome
  mapping. Both are v0.1 stubs; both should be calibrated once data
  exists.
- **A factory or upstream-spec change touches the schema, the rubric
  shape, or the ledger row format.** Any change to the on-disk
  contract gets reflected here so the doc and the validators do not
  drift.
- **Quarterly cadence review.** Even with no other trigger, re-read
  this document once a quarter. Cadence drift (skipping a month,
  doubling up two in a week) is the failure mode this exercise itself
  is most prone to.

## What this method is not

- Not a probability forecast. The pre-mortem names *what* could go
  wrong, not *with what probability*. The Brier-style score in spec
  0003 is on the trigger-fired binary, not on subjective odds.
- Not a substitute for thesis maintenance. The Thesis Pillar Tracker
  still owns "is the original thesis still true?". The pre-mortem
  ledger owns "what failure mode would the next 40-percent drawdown
  be written up as?".

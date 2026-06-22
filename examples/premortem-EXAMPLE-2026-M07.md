---
position: EXAMPLE
month: 2026-M07
exposure_tier: concentrated
failure_modes:
  - id: fm-1
    title: Top customer renegotiates contract terms downward
    narrative: |
      The position relies on a multi-year framework contract with its
      single largest customer. That customer signaled in their last
      earnings call that they are reviewing vendor spend. A renegotiation
      that resets pricing or shifts to a usage-based meter would compress
      gross margin enough to invalidate the original return model.
    rank: 1
    rubric_category: customer-concentration
    observability_triggers:
      - The customer's next earnings call names this vendor in a "vendor consolidation" or "cost discipline" section.
      - A new framework contract is filed with materially shorter duration than the prior one.
    status_log: []

  - id: fm-2
    title: Capital allocation pivots from buybacks to opportunistic M&A
    narrative: |
      The thesis assumes a steady share-count decline driven by the
      buyback program. Management has hinted at "tuck-in opportunities".
      If the board redirects free cash flow toward a sizeable
      acquisition at a premium multiple, the per-share compounding
      assumption collapses even if the underlying business is fine.
    rank: 2
    rubric_category: capital-allocation-regime
    observability_triggers:
      - Buyback authorization is reduced or paused at the next quarterly board action.
      - A press release announces an acquisition above 10 percent of market cap.
    status_log: []

  - id: fm-3
    title: Operating leverage reverses on flat revenue
    narrative: |
      The business added fixed cost during the last 18 months on the
      expectation of 20 percent topline growth. If revenue grows in the
      single digits next year, the same fixed cost base prints negative
      operating leverage and the consensus margin assumption misses by a
      wide margin.
    rank: 3
    rubric_category: operating-leverage-reversal
    observability_triggers:
      - Two consecutive quarters of revenue growth below 10 percent year over year.
      - Operating margin contracts more than 150 basis points sequentially without a one-time item.
    status_log: []
---

# Pre-Mortem: EXAMPLE, 2026-M07

You are writing this in early July 2026. The position has been the largest
exposure in the book for six weeks. Imagine it is mid-2027 and the
position is down 40 percent. The three failure modes above are the most
likely written-out reasons, ranked by your current read of the evidence.

Each mode names a concrete signal that, if observed, would mean the
hypothesis is no longer hypothetical. The `status_log` blocks are empty
because nothing has been re-scored yet. Run
`premortem status --month 2026-M08` next month to begin tracking.

## Why this example exists

This file is the worked example shipped with the v0.1 scaffold. The
ticker `EXAMPLE` is a placeholder; no real position is named. Replace
this file with the first real concentrated position before the August
run.

# Refresh the evidence without rewriting the pre-mortem

You wrote a failure mode before observing its outcome. Preserve that original
claim when a new source or note changes your view. Otherwise the ledger
gradually becomes a record of what you now believe you predicted.

For each monthly review, attach the dated source, the observable event it
supports, and the failure-mode identifier it bears on. Distinguish a primary
announcement from a later interpretation or a duplicate report of the same
announcement. Two notes that cite the same underlying filing supply one event.
An absence of new evidence should remain an absence. `unchanged` means the
trigger has not fired (`docs/METHODOLOGY.md`); record it after checking the
trigger's own source, and leave a quiet reading week out of the evidence.

Use separate roles for proposing an interpretation and checking its evidence.
The checker should read your original trigger and the primary material before
reading the proposed status. Then record whether the trigger is observed,
unobserved, contradicted, or unmeasurable with the available source. Map that
assessment to the status values the existing ledger actually supports: observed
is `observed`; partial evidence aligned with the trigger is `evidence-emerging`;
unobserved or contradicted, after checking the trigger's own source, is
`unchanged` with `--evidence` naming that source. No status fits an
unmeasurable trigger. Do not record it as `unchanged` or `retired`, since the
scorer counts both as a non-event; put the reason in a linked note. Retain
extra analysis in a linked note rather than inventing schema fields.

An illustrative failure mode is that a promised delivery slips past the dated
commitment. A later press release about a larger pipeline does not answer that
trigger. You need the delivery date or a documented reason it cannot be observed.
Likewise, a renamed product or revised target should not silently replace the
original event definition.

The protocol here changes evidence handling, not your positions or the threshold
for any financial action. The checked-in `EXAMPLE` corpus remains illustrative.
No real holding, new market observation, order, alert or investment
recommendation is created by this note.

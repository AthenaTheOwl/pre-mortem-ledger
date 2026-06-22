"""Calibration scoring.

A pre-mortem's `status_log` entries are the ground truth of how each
imagined failure mode actually played out. The Brier score reduces a
month of (predicted, observed) pairs to one number per run so the ledger
can record drift over time.

v0.1 ships the pure scoring helpers. Spec 0003 wires them into the
ledger via `premortem ledger score`, which will read the prior month's
file, derive the (predicted, observed) pairs, and write the result back
as `prior_run_brier` on the next ledger row.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from pre_mortem_ledger.schema import PreMortem, Status

# A failure mode whose trigger fired counts as a realized event.
# `unchanged` and `retired` are explicit non-events. `evidence-emerging`
# is treated as a half-credit signal: the pre-mortem named a signal that
# is starting to show up, but the binary outcome has not crossed.
_OUTCOME = {
    "unchanged": 0.0,
    "evidence-emerging": 0.5,
    "observed": 1.0,
    "retired": 0.0,
}


def brier_score(pairs: Sequence[Tuple[float, float]]) -> float:
    """Mean squared error of predicted probabilities against realized
    outcomes. Both must be in [0, 1]. Returns 0.0 for an empty input so
    a run with no prior pairs cannot poison the ledger with NaN.
    """
    if not pairs:
        return 0.0
    total = 0.0
    for predicted, observed in pairs:
        if not (0.0 <= predicted <= 1.0):
            raise ValueError(f"predicted probability out of range: {predicted}")
        if not (0.0 <= observed <= 1.0):
            raise ValueError(f"observed outcome out of range: {observed}")
        total += (predicted - observed) ** 2
    return total / len(pairs)


def outcome_for_status(status: Status) -> float:
    """Map a status_log status to its [0, 1] realized-outcome value."""
    if status not in _OUTCOME:
        raise ValueError(f"unknown status: {status!r}")
    return _OUTCOME[status]


def rank_to_prior(rank: int, n_modes: int) -> float:
    """Convert a 1..N rank to a prior probability that the trigger fires
    in the scoring window. Rank 1 (most likely) maps to the highest
    prior, rank N to the lowest. Linear schedule between 0.6 (rank 1 of 3)
    and 0.2 (rank 3 of 3).

    This is a deliberately simple v0.1 mapping. Spec 0003 may replace it
    with a calibrated mapping learned from prior months.
    """
    if n_modes < 1:
        raise ValueError("n_modes must be >= 1")
    if rank < 1 or rank > n_modes:
        raise ValueError(f"rank {rank} outside 1..{n_modes}")
    if n_modes == 1:
        return 0.5
    high, low = 0.6, 0.2
    step = (high - low) / (n_modes - 1)
    return high - step * (rank - 1)


def pairs_from_premortem(pm: PreMortem, month: str) -> List[Tuple[float, float]]:
    """Build (predicted, observed) pairs for one scoring month.

    `predicted` comes from the failure mode's rank via `rank_to_prior`.
    `observed` comes from the most recent `status_log` entry on or before
    `month`. Failure modes with no entry at or before `month` are skipped.
    """
    out: List[Tuple[float, float]] = []
    n = len(pm.failure_modes)
    for fm in pm.failure_modes:
        relevant = [e for e in fm.status_log if e.month <= month]
        if not relevant:
            continue
        latest = max(relevant, key=lambda e: e.month)
        predicted = rank_to_prior(fm.rank, n)
        observed = outcome_for_status(latest.status)
        out.append((predicted, observed))
    return out


def brier_for_month(pms: Iterable[PreMortem], month: str) -> float:
    """Brier across every pre-mortem's failure modes for `month`."""
    all_pairs: List[Tuple[float, float]] = []
    for pm in pms:
        all_pairs.extend(pairs_from_premortem(pm, month))
    return brier_score(all_pairs)

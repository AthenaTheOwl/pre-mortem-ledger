"""Golden-master locks for the calibration scoring helpers.

score.py has no other caller under test, so these pin the current output
of each helper to hand-computed literals. A future change to the Brier
formula or the rank-to-prior schedule fails here rather than silently
shifting every ledger's drift number.
"""

from __future__ import annotations

import pytest

from pre_mortem_ledger.score import (
    brier_score,
    outcome_for_status,
    pairs_from_premortem,
    rank_to_prior,
)


def test_brier_score_hand_computed():
    # ((1-0)^2 + (0-0)^2) / 2 = 0.5; dropping the square would give 0.5 too,
    # so use an asymmetric pair below to pin the exponent as well.
    assert brier_score([(1.0, 0.0), (0.0, 0.0)]) == 0.5


def test_brier_score_pins_the_square():
    # (0.5 - 0.0)^2 = 0.25; without the `** 2` this would be 0.5.
    assert brier_score([(0.5, 0.0)]) == 0.25


def test_brier_score_empty_is_zero():
    assert brier_score([]) == 0.0


@pytest.mark.parametrize("bad", [(-0.1, 0.0), (1.1, 0.0)])
def test_brier_score_predicted_out_of_range(bad):
    with pytest.raises(ValueError, match="predicted probability out of range"):
        brier_score([bad])


@pytest.mark.parametrize("bad", [(0.0, -0.1), (0.0, 1.1)])
def test_brier_score_observed_out_of_range(bad):
    with pytest.raises(ValueError, match="observed outcome out of range"):
        brier_score([bad])


def test_rank_to_prior_schedule():
    assert rank_to_prior(1, 3) == 0.6
    assert rank_to_prior(2, 3) == pytest.approx(0.4)
    assert rank_to_prior(3, 3) == 0.2


def test_rank_to_prior_single_mode():
    assert rank_to_prior(1, 1) == 0.5


def test_rank_to_prior_n_modes_guard():
    with pytest.raises(ValueError, match="n_modes must be >= 1"):
        rank_to_prior(1, 0)


def test_rank_to_prior_rank_out_of_range():
    with pytest.raises(ValueError, match="outside 1..3"):
        rank_to_prior(4, 3)


def test_outcome_for_status_each_status():
    assert outcome_for_status("unchanged") == 0.0
    assert outcome_for_status("evidence-emerging") == 0.5
    assert outcome_for_status("observed") == 1.0
    assert outcome_for_status("retired") == 0.0


def test_outcome_for_status_unknown():
    with pytest.raises(ValueError, match="unknown status"):
        outcome_for_status("bogus")  # type: ignore[arg-type]


def test_pairs_from_premortem_uses_latest_status(example_premortem):
    from pre_mortem_ledger.schema import append_status

    # fm-2 gets an "observed" entry in 2026-M08; the other two have no log.
    pm = append_status(
        example_premortem,
        month="2026-M08",
        status="observed",
        failure_mode_ids=["fm-2"],
    )
    pairs = pairs_from_premortem(pm, "2026-M08")
    # only fm-2 has an entry on/before the month; rank 2 of 3 -> prior 0.4.
    assert pairs == [(pytest.approx(0.4), 1.0)]

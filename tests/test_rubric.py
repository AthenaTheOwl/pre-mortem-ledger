"""Rubric loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pre_mortem_ledger.rubric import assert_categories_known, load_rubric


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_shipped_rubric_has_at_least_eight_categories():
    rubric = load_rubric(REPO_ROOT / "rubric" / "failure_modes.yaml")
    assert len(rubric) >= 8


def test_example_categories_are_known():
    rubric = load_rubric(REPO_ROOT / "rubric" / "failure_modes.yaml")
    used = [
        "customer-concentration",
        "capital-allocation-regime",
        "operating-leverage-reversal",
    ]
    assert_categories_known(used, rubric)


def test_unknown_category_is_rejected():
    rubric = load_rubric(REPO_ROOT / "rubric" / "failure_modes.yaml")
    with pytest.raises(ValueError, match="unknown rubric categories"):
        assert_categories_known(["not-a-real-category"], rubric)

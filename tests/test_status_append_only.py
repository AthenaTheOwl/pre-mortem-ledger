"""Append-only status_log tests (R-PML-006)."""

from __future__ import annotations

import pytest

from pre_mortem_ledger.schema import append_status


def test_append_adds_one_entry_per_mode(example_premortem):
    updated = append_status(example_premortem, month="2026-M08", status="unchanged")
    for fm in updated.failure_modes:
        assert len(fm.status_log) == 1
        assert fm.status_log[0].month == "2026-M08"


def test_append_targets_one_mode(example_premortem):
    updated = append_status(
        example_premortem,
        month="2026-M08",
        status="observed",
        evidence_ref="https://example.com/8-k",
        failure_mode_ids=["fm-2"],
    )
    counts = {fm.id: len(fm.status_log) for fm in updated.failure_modes}
    assert counts == {"fm-1": 0, "fm-2": 1, "fm-3": 0}
    fm2 = next(fm for fm in updated.failure_modes if fm.id == "fm-2")
    assert fm2.status_log[0].status == "observed"
    assert fm2.status_log[0].evidence_ref == "https://example.com/8-k"


def test_double_append_same_month_rejected(example_premortem):
    once = append_status(example_premortem, month="2026-M08", status="unchanged")
    with pytest.raises(ValueError, match="already has a status_log entry"):
        append_status(once, month="2026-M08", status="evidence-emerging")


def test_append_does_not_mutate_input(example_premortem):
    snapshot = example_premortem.model_dump_json()
    _ = append_status(example_premortem, month="2026-M08", status="unchanged")
    assert example_premortem.model_dump_json() == snapshot

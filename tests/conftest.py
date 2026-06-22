"""Test fixtures for the Pre-Mortem Ledger.

These fixtures build PreMortem objects in memory so individual tests don't
have to redeclare the same valid shape.
"""

from __future__ import annotations

import pytest

from pre_mortem_ledger.schema import FailureMode, PreMortem


@pytest.fixture
def minimal_failure_modes() -> list[FailureMode]:
    return [
        FailureMode(
            id=f"fm-{i}",
            title=f"Failure mode {i}",
            rank=i,
            narrative="A long enough narrative to satisfy the schema validator.",
            rubric_category="thesis-pillar-invalidation",
            observability_triggers=["A concrete observable signal."],
            status_log=[],
        )
        for i in (1, 2, 3)
    ]


@pytest.fixture
def example_premortem(minimal_failure_modes) -> PreMortem:
    return PreMortem(
        position="EXAMPLE",
        month="2026-M07",
        exposure_tier="concentrated",
        failure_modes=minimal_failure_modes,
    )

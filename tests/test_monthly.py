"""Tests for the monthly runner.

Covers:
- `load_positions` reads the shipped `config/positions.yaml`
- `pick_target` prefers concentrated over sized over probe
- `scaffold_premortem` writes a file whose name matches the convention
  and whose body round-trips through the schema validator
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pre_mortem_ledger.monthly import (
    Position,
    load_positions,
    pick_target,
    scaffold_premortem,
)
from pre_mortem_ledger.schema import load_premortem_file


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_load_positions_reads_shipped_file():
    positions = load_positions(REPO_ROOT / "config" / "positions.yaml")
    assert any(p.ticker == "EXAMPLE" for p in positions)


def test_pick_target_prefers_concentrated():
    positions = [
        Position("PROBE", "probe", "2025-01"),
        Position("SIZED", "sized", "2024-12"),
        Position("CONC", "concentrated", "2026-04"),
    ]
    assert pick_target(positions).ticker == "CONC"


def test_pick_target_empty_raises():
    with pytest.raises(ValueError):
        pick_target([])


def test_scaffold_writes_valid_file(tmp_path):
    out = scaffold_premortem(
        month="2026-M09", position="EXAMPLE", out_dir=tmp_path
    )
    assert out.name == "premortem-EXAMPLE-2026-M09.md"
    pm = load_premortem_file(out)
    assert pm.month == "2026-M09"
    assert len(pm.failure_modes) == 3
    assert all(fm.status_log == [] for fm in pm.failure_modes)


def test_scaffold_filename_round_trip(tmp_path):
    out = scaffold_premortem(month="2026-M12", position="ABC", out_dir=tmp_path)
    pm = load_premortem_file(out)
    assert pm.expected_filename() == out.name

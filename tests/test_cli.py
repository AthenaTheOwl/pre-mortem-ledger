"""End-to-end CLI tests.

Exercises the four verbs (`new`, `status`, `render`, `ledger record`)
against a tmp_path-based working tree so the tests do not write into the
real repo.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from pre_mortem_ledger.cli import main
from pre_mortem_ledger.ledger import read_ledger
from pre_mortem_ledger.schema import load_premortem_file


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def workspace(tmp_path) -> Path:
    """A tmp working tree with the rubric, schema, and a positions file."""
    (tmp_path / "config").mkdir()
    (tmp_path / "rubric").mkdir()
    shutil.copy(REPO_ROOT / "config" / "positions.yaml", tmp_path / "config" / "positions.yaml")
    shutil.copy(REPO_ROOT / "rubric" / "failure_modes.yaml", tmp_path / "rubric" / "failure_modes.yaml")
    return tmp_path


def test_cli_new_writes_scaffold(workspace, monkeypatch, capsys):
    monkeypatch.chdir(workspace)
    rc = main(["new", "--month", "2026-M07"])
    assert rc == 0
    out_path = workspace / "premortem" / "premortem-EXAMPLE-2026-M07.md"
    assert out_path.exists()
    pm = load_premortem_file(out_path)
    assert pm.position == "EXAMPLE"


def test_cli_status_appends_entry(workspace, monkeypatch):
    monkeypatch.chdir(workspace)
    assert main(["new", "--month", "2026-M07"]) == 0
    file = workspace / "premortem" / "premortem-EXAMPLE-2026-M07.md"
    assert (
        main(
            [
                "status",
                "--file",
                str(file),
                "--month",
                "2026-M08",
                "--id",
                "fm-1",
                "--set",
                "evidence-emerging",
                "--note",
                "first signal",
            ]
        )
        == 0
    )
    pm = load_premortem_file(file)
    fm1 = next(fm for fm in pm.failure_modes if fm.id == "fm-1")
    assert len(fm1.status_log) == 1
    assert fm1.status_log[0].status == "evidence-emerging"


def test_cli_render_writes_index(workspace, monkeypatch):
    monkeypatch.chdir(workspace)
    assert main(["new", "--month", "2026-M07"]) == 0
    assert main(["render", "--month", "2026-M07"]) == 0
    index = workspace / "premortem" / "INDEX.md"
    assert index.exists()
    text = index.read_text(encoding="utf-8")
    assert "EXAMPLE" in text
    assert "2026-M07" in text


def test_cli_ledger_record_appends_row(workspace, monkeypatch):
    monkeypatch.chdir(workspace)
    rc = main(
        [
            "ledger",
            "record",
            "--month",
            "2026-M07",
            "--type",
            "monthly",
            "--positions",
            "EXAMPLE",
            "--modes",
            "3",
            "--notes",
            "first real monthly run",
        ]
    )
    assert rc == 0
    rows = read_ledger(workspace / "data" / "ledger" / "runs.jsonl")
    assert len(rows) == 1
    assert rows[0].run_id == "2026-M07-monthly"
    assert rows[0].positions_scored == ["EXAMPLE"]


def test_cli_ledger_record_refuses_duplicate(workspace, monkeypatch):
    monkeypatch.chdir(workspace)
    args = [
        "ledger",
        "record",
        "--month",
        "2026-M07",
        "--type",
        "monthly",
        "--positions",
        "EXAMPLE",
        "--modes",
        "3",
    ]
    assert main(args) == 0
    with pytest.raises(ValueError, match="already"):
        main(args)


def test_cli_show_prints_ranked_snapshot(capsys):
    rc = main(["show"])
    assert rc == 0
    out = capsys.readouterr().out
    # header + the committed example position
    assert "pre-mortem" in out
    assert "EXAMPLE" in out
    # ranked failure modes appear in rank order
    assert "fm-1" in out and "fm-2" in out and "fm-3" in out
    assert out.index("fm-1") < out.index("fm-2") < out.index("fm-3")
    # the ledger row shows up
    assert "initialization" in out
    # a headline finding is rendered, not just raw data
    assert "headline:" in out
    # ASCII-only so it renders cleanly in any terminal codepage
    out.encode("ascii")


def test_cli_show_handles_missing_premortem(tmp_path, capsys):
    rc = main(["show", "--file", str(tmp_path / "nope.md")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "no committed pre-mortem" in out or "premortem new" in out


def test_shipped_ledger_row_is_well_formed():
    rows = read_ledger(REPO_ROOT / "data" / "ledger" / "runs.jsonl")
    assert len(rows) == 1
    row = rows[0]
    assert row.run_type == "initialization"
    assert row.month == "2026-M06"
    assert row.prior_run_brier is None
    raw = (REPO_ROOT / "data" / "ledger" / "runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(raw) == 1
    json.loads(raw[0])

"""Schema tests.

Coverage:
- round-trip through `dump_premortem_file` / `load_premortem_file`
- required-field rejections
- the `min 3 failure modes` rule
- empty `status_log` is accepted at creation
- unique `id` and contiguous `rank` rules
- the worked example in `examples/` parses and validates
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from pre_mortem_ledger.schema import (
    FailureMode,
    PreMortem,
    StatusLogEntry,
    dump_premortem_file,
    load_premortem_file,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_FILE = REPO_ROOT / "examples" / "premortem-EXAMPLE-2026-M07.md"
SCHEMA_FILE = REPO_ROOT / "schemas" / "premortem.schema.json"


def test_round_trip(tmp_path, example_premortem):
    out = tmp_path / "premortem-EXAMPLE-2026-M07.md"
    dump_premortem_file(example_premortem, out, body="# header\n")
    reloaded = load_premortem_file(out)
    assert reloaded == example_premortem


def test_filename_convention(example_premortem):
    assert example_premortem.expected_filename() == "premortem-EXAMPLE-2026-M07.md"


def test_minimum_failure_modes(example_premortem):
    with pytest.raises(ValidationError):
        PreMortem(
            position=example_premortem.position,
            month=example_premortem.month,
            failure_modes=example_premortem.failure_modes[:2],
        )


def test_status_log_starts_empty(example_premortem):
    for fm in example_premortem.failure_modes:
        assert fm.status_log == []


def test_month_format_rejected():
    with pytest.raises(ValidationError):
        PreMortem(position="EXAMPLE", month="2026-07", failure_modes=[])


def test_ticker_format_rejected():
    with pytest.raises(ValidationError):
        PreMortem(
            position="lowercase",
            month="2026-M07",
            failure_modes=[
                FailureMode(
                    id=f"fm-{i}",
                    title="t",
                    rank=i,
                    narrative="x" * 30,
                    rubric_category="thesis-pillar-invalidation",
                    observability_triggers=["x"],
                )
                for i in (1, 2, 3)
            ],
        )


def test_duplicate_failure_mode_ids(minimal_failure_modes):
    minimal_failure_modes[1] = minimal_failure_modes[1].model_copy(
        update={"id": minimal_failure_modes[0].id}
    )
    with pytest.raises(ValidationError):
        PreMortem(
            position="EXAMPLE", month="2026-M07", failure_modes=minimal_failure_modes
        )


def test_ranks_must_be_contiguous(minimal_failure_modes):
    minimal_failure_modes[2] = minimal_failure_modes[2].model_copy(update={"rank": 5})
    with pytest.raises(ValidationError):
        PreMortem(
            position="EXAMPLE", month="2026-M07", failure_modes=minimal_failure_modes
        )


def test_status_log_monotonic_months():
    with pytest.raises(ValidationError):
        FailureMode(
            id="fm-1",
            title="title",
            rank=1,
            narrative="x" * 30,
            rubric_category="thesis-pillar-invalidation",
            observability_triggers=["x"],
            status_log=[
                StatusLogEntry(month="2026-M08", status="unchanged"),
                StatusLogEntry(month="2026-M07", status="unchanged"),
            ],
        )


def test_example_file_parses():
    pm = load_premortem_file(EXAMPLE_FILE)
    assert pm.position == "EXAMPLE"
    assert pm.month == "2026-M07"
    assert len(pm.failure_modes) == 3


def test_json_schema_is_well_formed():
    raw = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(raw)


def test_example_validates_against_json_schema():
    raw = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    pm = load_premortem_file(EXAMPLE_FILE)
    payload = pm.model_dump(mode="json", exclude_none=True)
    jsonschema.Draft202012Validator(raw).validate(payload)

"""Pydantic mirror of `schemas/premortem.schema.json`.

Markdown pre-mortem files carry the structured data in a YAML front-matter
block. The body below the closing `---` is free-form narrative for the
human reader and is not part of the schema-validated payload.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MONTH_PATTERN = re.compile(r"^[0-9]{4}-M(0[1-9]|1[0-2])$")
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9]{0,7}$")

Status = Literal["unchanged", "evidence-emerging", "observed", "retired"]
ExposureTier = Literal["concentrated", "sized", "probe"]


class StatusLogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: str
    status: Status
    evidence_ref: Optional[str] = None
    note: Optional[str] = None

    @field_validator("month")
    @classmethod
    def _check_month(cls, v: str) -> str:
        if not MONTH_PATTERN.match(v):
            raise ValueError(f"month must look like 2026-M07, got {v!r}")
        return v


class FailureMode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^fm-[0-9]{1,3}$")
    title: str = Field(min_length=4)
    narrative: str = Field(min_length=20)
    rank: int = Field(ge=1, le=10)
    rubric_category: str
    observability_triggers: List[str] = Field(min_length=1)
    status_log: List[StatusLogEntry] = Field(default_factory=list)

    @field_validator("observability_triggers")
    @classmethod
    def _non_empty_triggers(cls, v: List[str]) -> List[str]:
        for t in v:
            if not t.strip():
                raise ValueError("observability triggers must be non-empty strings")
        return v

    @model_validator(mode="after")
    def _status_log_monotonic(self) -> "FailureMode":
        months = [entry.month for entry in self.status_log]
        if months != sorted(months):
            raise ValueError(
                f"status_log months must be ascending; got {months}"
            )
        if len(months) != len(set(months)):
            raise ValueError(
                f"status_log must have at most one entry per month; got {months}"
            )
        return self


class PreMortem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position: str
    month: str
    exposure_tier: ExposureTier = "concentrated"
    failure_modes: List[FailureMode] = Field(min_length=3, max_length=8)

    @field_validator("position")
    @classmethod
    def _check_ticker(cls, v: str) -> str:
        if not TICKER_PATTERN.match(v):
            raise ValueError(f"position must look like a ticker, got {v!r}")
        return v

    @field_validator("month")
    @classmethod
    def _check_month(cls, v: str) -> str:
        if not MONTH_PATTERN.match(v):
            raise ValueError(f"month must look like 2026-M07, got {v!r}")
        return v

    @model_validator(mode="after")
    def _unique_failure_mode_ids(self) -> "PreMortem":
        ids = [fm.id for fm in self.failure_modes]
        if len(ids) != len(set(ids)):
            raise ValueError(f"failure_modes must have unique ids; got {ids}")
        ranks = sorted(fm.rank for fm in self.failure_modes)
        expected = list(range(1, len(ranks) + 1))
        if ranks != expected:
            raise ValueError(
                f"failure_modes ranks must be 1..N contiguous; got {ranks}"
            )
        return self

    def expected_filename(self) -> str:
        return f"premortem-{self.position}-{self.month}.md"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("file must start with a YAML front-matter block (`---`)")
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        raise ValueError("front-matter block is not terminated")
    head = parts[0][3:]
    body = parts[1].lstrip("\n") if len(parts) == 2 else parts[1].lstrip("\n")
    data = yaml.safe_load(head) or {}
    return data, body


def load_premortem_file(path: str | Path) -> PreMortem:
    """Parse and validate a Markdown pre-mortem file."""
    raw = Path(path).read_text(encoding="utf-8")
    data, _body = _split_frontmatter(raw)
    return PreMortem.model_validate(data)


def dump_premortem_file(pm: PreMortem, path: str | Path, body: str = "") -> Path:
    """Write a pre-mortem to disk as YAML front-matter + Markdown body.

    The body is written verbatim. The schema payload is dumped with
    `yaml.safe_dump` so the on-disk shape is stable across runs.
    """
    payload = pm.model_dump(mode="json", exclude_none=True)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    serialized = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    text = f"---\n{serialized}---\n\n{body.strip()}\n" if body.strip() else f"---\n{serialized}---\n"
    out.write_text(text, encoding="utf-8")
    return out


def append_status(
    pm: PreMortem,
    month: str,
    status: Status,
    *,
    evidence_ref: Optional[str] = None,
    note: Optional[str] = None,
    failure_mode_ids: Optional[Iterable[str]] = None,
) -> PreMortem:
    """Return a new PreMortem with a new status_log entry appended to each
    targeted failure mode. The original object is not mutated.

    Append-only: refuses to overwrite an existing entry for the same
    (failure_mode_id, month) pair.
    """
    targets = set(failure_mode_ids) if failure_mode_ids is not None else None
    new_modes: List[FailureMode] = []
    for fm in pm.failure_modes:
        if targets is not None and fm.id not in targets:
            new_modes.append(fm)
            continue
        existing_months = {e.month for e in fm.status_log}
        if month in existing_months:
            raise ValueError(
                f"failure_mode {fm.id} already has a status_log entry for {month}"
            )
        new_entry = StatusLogEntry(
            month=month, status=status, evidence_ref=evidence_ref, note=note
        )
        new_modes.append(
            fm.model_copy(update={"status_log": [*fm.status_log, new_entry]})
        )
    return pm.model_copy(update={"failure_modes": new_modes})

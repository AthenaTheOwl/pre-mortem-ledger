# Spec 0001 — Tasks

Ordered for the first 2-3 PRs after the scaffold lands.

## PR 1 — schema and rubric

- [ ] Write `schemas/premortem.schema.json` (R-PML-002).
- [ ] Write `src/premortem/schema.py` Pydantic mirror.
- [ ] Write `config/positions.yaml` with one `EXAMPLE` row (R-PML-003).
- [ ] Write `rubric/failure_modes.yaml` with 8-12 categories (R-PML-004).
- [ ] Write `tests/test_schema.py` covering round-trip + required fields.
- [ ] Write `examples/premortem-EXAMPLE-2026-M07.md` (R-PML-007).

## PR 2 — CLI and monthly runner

- [ ] Write `src/premortem/cli.py` with `new`, `status`, `render`.
- [ ] Write `src/premortem/monthly.py` (picks position, scaffolds file).
- [ ] Enforce filename convention (R-PML-005) in CLI + tests.
- [ ] Write `tests/test_monthly.py`.
- [ ] Write `tests/test_status_append_only.py` (R-PML-006).
- [ ] Document the `new / status / render` flow in README.

## PR 3 — gates

- [ ] Copy `scripts/voice_lint.py` from the portfolio voice spec
      (R-PML-008).
- [ ] Write `scripts/spec_check.py` (R-PML-009).
- [ ] Add `pyproject.toml` with `uv` + `pytest` + `ruff`.
- [ ] Wire CI (deferred to spec 0002; just leave a TODO in this PR).
- [ ] Confirm the example pre-mortem passes voice_lint stub.

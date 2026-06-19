# First PR after the scaffold

Title: `feat: pre-mortem schema, rubric, example`

## Scope

This PR lands the typed substrate. No CLI yet, no rendering yet. The
goal is that one schema-validated example pre-mortem exists in the
repo, so the next PR can stand on a stable shape.

## Files added

- `schemas/premortem.schema.json` — JSON Schema for one pre-mortem.
  Required fields: `position`, `month`, `failure_modes[]` (min 3).
  Each failure mode requires `id`, `title`, `narrative`, `rank`,
  `observability_triggers[]` (min 1), and an append-only
  `status_log[]` (may be empty at creation).
- `src/premortem/__init__.py`
- `src/premortem/schema.py` — Pydantic mirror of the JSON Schema.
- `config/positions.yaml` — one placeholder row:
  `{ticker: EXAMPLE, exposure_tier: concentrated, since: 2026-06}`.
- `rubric/failure_modes.yaml` — 8-12 categories with `id`,
  `name`, `description`. Categories include
  `thesis-pillar-invalidation`, `capital-allocation-regime`,
  `operating-leverage-reversal`, `sector-rotation`,
  `regulatory-hit`, `key-person`, `secondary-supply-shock`,
  `narrative-mean-reversion`.
- `examples/premortem-EXAMPLE-2026-M07.md` — worked example
  with 3 failure modes, each tagged to a rubric category, each
  with one observability trigger and an empty `status_log`.
- `tests/test_schema.py` — round-trip tests, required-field tests,
  the `min 3 failure modes` rule, and the empty-status-log creation
  case.
- `pyproject.toml` — `uv` + `pytest` + `pydantic` + `pyyaml` +
  `jsonschema` + `ruff`.

## Files changed

None. This is the first PR after the scaffold.

## Verification

```bash
uv sync
uv run pytest -v
uv run python -c "import json, jsonschema; \
  schema=json.load(open('schemas/premortem.schema.json')); \
  jsonschema.Draft202012Validator.check_schema(schema)"
```

All three commands exit zero. `pytest -v` shows at least 6 passing
tests covering schema validation and the append-only rule.

## What this PR does not do

- No CLI. The `premortem new / status / render` commands ship in
  PR 2 (R-PML-005, R-PML-006 enforcement).
- No voice_lint copy. The portfolio voice script lands in PR 3
  (R-PML-008).
- No CI workflow. Deferred to spec 0002.

## Review checklist

- [ ] JSON Schema validates against Draft 2020-12 meta-schema.
- [ ] Pydantic mirror does not drift from the JSON Schema (the
      round-trip test pins this).
- [ ] The example pre-mortem uses ticker `EXAMPLE` and no real
      position is named.
- [ ] Every failure mode in the example is tagged to a rubric
      category that exists in `rubric/failure_modes.yaml`.

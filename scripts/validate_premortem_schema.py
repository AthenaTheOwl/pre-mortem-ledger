#!/usr/bin/env python3
"""Validate one or more pre-mortem Markdown files against the JSON Schema
and the failure-mode rubric.

Usage:
    python scripts/validate_premortem_schema.py <path> [<path> ...]

Exit code is 0 if every file validates, 1 if any file fails, 2 on usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

from pre_mortem_ledger.rubric import assert_categories_known, load_rubric
from pre_mortem_ledger.schema import load_premortem_file


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "premortem.schema.json"
RUBRIC_PATH = REPO_ROOT / "rubric" / "failure_modes.yaml"


def validate_one(
    path: Path,
    schema_validator: jsonschema.Draft202012Validator,
    rubric: dict,
) -> list[str]:
    errs: list[str] = []
    try:
        pm = load_premortem_file(path)
    except Exception as exc:
        errs.append(f"{path}: parse failed: {exc}")
        return errs
    payload = pm.model_dump(mode="json", exclude_none=True)
    for err in sorted(schema_validator.iter_errors(payload), key=lambda e: e.path):
        errs.append(f"{path}: schema: {'/'.join(map(str, err.path)) or '<root>'}: {err.message}")
    expected_name = pm.expected_filename()
    if path.name != expected_name:
        errs.append(f"{path}: filename does not match convention; expected {expected_name}")
    try:
        assert_categories_known(
            [fm.rubric_category for fm in pm.failure_modes], rubric
        )
    except ValueError as exc:
        errs.append(f"{path}: rubric: {exc}")
    return errs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)

    raw_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(raw_schema)
    validator = jsonschema.Draft202012Validator(raw_schema)
    rubric = load_rubric(RUBRIC_PATH)

    total_errs = 0
    for p in args.paths:
        errs = validate_one(Path(p), validator, rubric)
        for e in errs:
            print(e)
        total_errs += len(errs)
    if total_errs:
        print(f"\nvalidate_premortem_schema: {total_errs} error(s)", file=sys.stderr)
        return 1
    print("validate_premortem_schema: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

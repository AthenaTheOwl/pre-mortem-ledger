"""`premortem` CLI.

Three verbs cover the monthly loop:

    premortem new      --month YYYY-Mnn [--position TICKER]
    premortem status   --month YYYY-Mnn --id fm-N --set STATUS [...]
    premortem render   --month YYYY-Mnn

Plus the ledger surface for the control-plane framing:

    premortem ledger list
    premortem ledger record --month YYYY-Mnn --type {initialization,monthly,calibration}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from pre_mortem_ledger.ledger import (
    DEFAULT_LEDGER_PATH,
    LedgerRow,
    append_ledger,
    read_ledger,
)
from pre_mortem_ledger.monthly import (
    DEFAULT_POSITIONS_PATH,
    DEFAULT_PREMORTEM_DIR,
    load_positions,
    pick_target,
    scaffold_premortem,
)
from pre_mortem_ledger.report import format_ledger_rows, render_month_index
from pre_mortem_ledger.schema import (
    append_status,
    dump_premortem_file,
    load_premortem_file,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="premortem", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="scaffold a new monthly pre-mortem")
    p_new.add_argument("--month", required=True)
    p_new.add_argument("--position", default=None)
    p_new.add_argument("--positions-file", default=str(DEFAULT_POSITIONS_PATH))
    p_new.add_argument("--out-dir", default=str(DEFAULT_PREMORTEM_DIR))

    p_status = sub.add_parser("status", help="append a status_log entry")
    p_status.add_argument("--file", required=True)
    p_status.add_argument("--month", required=True)
    p_status.add_argument("--id", dest="fm_id", required=True)
    p_status.add_argument(
        "--set",
        dest="status",
        required=True,
        choices=["unchanged", "evidence-emerging", "observed", "retired"],
    )
    p_status.add_argument("--evidence", default=None)
    p_status.add_argument("--note", default=None)

    p_render = sub.add_parser("render", help="render a per-month INDEX.md")
    p_render.add_argument("--month", required=True)
    p_render.add_argument("--in-dir", default=str(DEFAULT_PREMORTEM_DIR))
    p_render.add_argument("--out", default=None)

    p_validate = sub.add_parser(
        "validate",
        help="validate bundled pre-mortem examples against schema + rubric",
    )
    p_validate.add_argument(
        "paths",
        nargs="*",
        default=None,
        help="pre-mortem files to validate; defaults to the bundled examples/",
    )

    p_ledger = sub.add_parser("ledger", help="ledger of scoring runs")
    ledger_sub = p_ledger.add_subparsers(dest="ledger_cmd", required=True)

    p_ledger_list = ledger_sub.add_parser("list")
    p_ledger_list.add_argument("--path", default=str(DEFAULT_LEDGER_PATH))

    p_ledger_record = ledger_sub.add_parser("record")
    p_ledger_record.add_argument("--month", required=True)
    p_ledger_record.add_argument(
        "--type",
        dest="run_type",
        default="monthly",
        choices=["initialization", "monthly", "calibration"],
    )
    p_ledger_record.add_argument("--positions", nargs="*", default=[])
    p_ledger_record.add_argument("--modes", type=int, default=0)
    p_ledger_record.add_argument("--brier", type=float, default=None)
    p_ledger_record.add_argument("--notes", default="")
    p_ledger_record.add_argument("--path", default=str(DEFAULT_LEDGER_PATH))

    return p


def _cmd_new(args: argparse.Namespace) -> int:
    if args.position is None:
        positions = load_positions(args.positions_file)
        target = pick_target(positions)
        ticker, tier = target.ticker, target.exposure_tier
    else:
        ticker, tier = args.position, "concentrated"
    out = scaffold_premortem(
        month=args.month, position=ticker, out_dir=args.out_dir, exposure_tier=tier
    )
    print(str(out))
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    pm = load_premortem_file(args.file)
    updated = append_status(
        pm,
        month=args.month,
        status=args.status,
        evidence_ref=args.evidence,
        note=args.note,
        failure_mode_ids=[args.fm_id],
    )
    dump_premortem_file(updated, args.file)
    print(f"appended {args.status} for {args.fm_id} at {args.month}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        out_path = render_month_index(
            args.month, in_dir=args.in_dir, out_path=args.out
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(str(out_path))
    return 0


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "premortem.schema.json"
RUBRIC_PATH = REPO_ROOT / "rubric" / "failure_modes.yaml"
DEFAULT_EXAMPLES_DIR = REPO_ROOT / "examples"


def _validate_one(path, validator, rubric) -> list[str]:
    from pre_mortem_ledger.rubric import assert_categories_known
    from pre_mortem_ledger.schema import load_premortem_file

    errs: list[str] = []
    try:
        pm = load_premortem_file(path)
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: parse failed: {exc}"]
    payload = pm.model_dump(mode="json", exclude_none=True)
    for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
        errs.append(f"{path}: schema: {'/'.join(map(str, err.path)) or '<root>'}: {err.message}")
    expected_name = pm.expected_filename()
    if Path(path).name != expected_name:
        errs.append(f"{path}: filename does not match convention; expected {expected_name}")
    try:
        assert_categories_known([fm.rubric_category for fm in pm.failure_modes], rubric)
    except ValueError as exc:
        errs.append(f"{path}: rubric: {exc}")
    return errs


def _cmd_validate(args: argparse.Namespace) -> int:
    import jsonschema

    from pre_mortem_ledger.rubric import load_rubric

    paths = list(args.paths) if args.paths else sorted(
        str(p) for p in DEFAULT_EXAMPLES_DIR.glob("premortem-*.md")
    )
    if not paths:
        print("validate: no example pre-mortems found", file=sys.stderr)
        return 1

    raw_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(raw_schema)
    validator = jsonschema.Draft202012Validator(raw_schema)
    rubric = load_rubric(RUBRIC_PATH)

    total = 0
    for p in paths:
        for err in _validate_one(p, validator, rubric):
            print(err)
            total += 1
    if total:
        print(f"\nvalidate: {total} error(s)", file=sys.stderr)
        return 1
    print(f"validate: clean ({len(paths)} file(s))")
    return 0


def _cmd_ledger_list(args: argparse.Namespace) -> int:
    rows = read_ledger(args.path)
    if not rows:
        print("ledger is empty")
        return 0
    for line in format_ledger_rows(rows):
        print(line)
    return 0


def _cmd_ledger_record(args: argparse.Namespace) -> int:
    run_id = f"{args.month}-{args.run_type}"
    row = LedgerRow(
        run_id=run_id,
        month=args.month,
        run_type=args.run_type,
        positions_scored=list(args.positions),
        failure_modes_logged=args.modes,
        prior_run_brier=args.brier,
        notes=args.notes,
    )
    out = append_ledger(row, args.path)
    print(f"recorded {run_id} -> {out}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "new":
        return _cmd_new(args)
    if args.cmd == "status":
        return _cmd_status(args)
    if args.cmd == "render":
        return _cmd_render(args)
    if args.cmd == "validate":
        return _cmd_validate(args)
    if args.cmd == "ledger":
        if args.ledger_cmd == "list":
            return _cmd_ledger_list(args)
        if args.ledger_cmd == "record":
            return _cmd_ledger_record(args)
    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

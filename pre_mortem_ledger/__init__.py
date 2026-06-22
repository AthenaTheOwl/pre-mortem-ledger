"""Pre-Mortem Ledger — typed monthly pre-mortem write-ups and a ledger of
calibration runs against the user's largest active investing position.

Public surface is small on purpose: the schema, the CLI entry point, and a
couple of helpers for loading positions and the failure-mode rubric.
"""

from pre_mortem_ledger.schema import (
    FailureMode,
    PreMortem,
    StatusLogEntry,
    load_premortem_file,
    dump_premortem_file,
)

__all__ = [
    "FailureMode",
    "PreMortem",
    "StatusLogEntry",
    "load_premortem_file",
    "dump_premortem_file",
    "__version__",
]

__version__ = "0.1.0"

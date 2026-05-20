"""Persistence helpers using ``os``, ``json`` and ``csv``."""

from __future__ import annotations

import csv
import json
import os
from typing import Any, Dict

from core.report import Report


def ensure_dir(path: str) -> None:
    """Create *path* if it doesn't already exist (no error if it does)."""
    os.makedirs(path, exist_ok=True)


def report_to_json(report: Report, output_dir: str) -> str:
    """Save *report* as a JSON file under *output_dir*.

    Returns:
        The absolute path to the file that was written.
    """
    ensure_dir(output_dir)
    filename = _make_filename(report, ".json")
    full_path = os.path.join(output_dir, filename)
    payload = report.to_dict()
    try:
        with open(full_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
    except OSError as exc:
        raise OSError(f"Failed to write JSON report to {full_path}: {exc}") from exc
    return os.path.abspath(full_path)


def report_to_csv(report: Report, output_dir: str) -> str:
    """Save *report* as a flat CSV file under *output_dir*.

    Each analyzer becomes a section of rows: ``analyzer, key, value``. Lists
    and tuples are joined with ``|`` so the resulting file stays one cell
    per value.

    Returns:
        The absolute path to the file that was written.
    """
    ensure_dir(output_dir)
    filename = _make_filename(report, ".csv")
    full_path = os.path.join(output_dir, filename)
    try:
        with open(full_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["book_title", report.book.title])
            writer.writerow(["book_author", report.book.author])
            writer.writerow(["created_at", report.created_at])
            writer.writerow([])
            writer.writerow(["analyzer", "key", "value"])
            for analyzer_name, result in report.results.items():
                if isinstance(result, dict):
                    for key, value in result.items():
                        writer.writerow([analyzer_name, key, _flatten(value)])
                else:
                    writer.writerow([analyzer_name, "result", _flatten(result)])
    except OSError as exc:
        raise OSError(f"Failed to write CSV report to {full_path}: {exc}") from exc
    return os.path.abspath(full_path)


# ---------------------------------------------------------------------- #
# helpers
# ---------------------------------------------------------------------- #
def _make_filename(report: Report, extension: str) -> str:
    """Build a filesystem-safe filename like ``report_<title>_<ts>.json``."""
    safe_title = "".join(
        ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in report.book.title
    )
    timestamp = report.created_at.replace(":", "").replace("-", "")
    return f"report_{safe_title}_{timestamp}{extension}"


def _flatten(value: Any) -> str:
    """Render a value as a single CSV cell."""
    if isinstance(value, (list, tuple)):
        return "|".join(_flatten(item) for item in value)
    if isinstance(value, dict):
        return "|".join(f"{k}={_flatten(v)}" for k, v in value.items())
    return str(value)

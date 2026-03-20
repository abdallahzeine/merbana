from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deepdiff import DeepDiff

from .importer import QuarantineRecord
from .validators import ValidationIssue


def _canonicalize(data: Any) -> Any:
    if isinstance(data, dict):
        out: dict[str, Any] = {}
        for key in sorted(data):
            value = _canonicalize(data[key])
            if value is None:
                continue
            out[key] = value
        return out
    if isinstance(data, list):
        canon = [_canonicalize(v) for v in data]
        canon.sort(key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False))
        return canon
    return data


def write_counts_artifact(
    path: Path,
    source_counts: dict[str, int],
    imported_counts: dict[str, int],
    quarantined: list[QuarantineRecord],
    validation_issues: list[ValidationIssue],
    dry_run: bool,
    source_file: str,
    db_path: str,
) -> dict[str, Any]:
    mismatch_details = []
    for key in sorted(source_counts):
        s = source_counts.get(key, 0)
        i = imported_counts.get(key, 0)
        if s != i:
            mismatch_details.append(
                {
                    "entity": key,
                    "source": s,
                    "imported": i,
                    "difference": s - i,
                    "explanation": "Mismatch caused by quarantined or invalid records",
                }
            )

    q_counter = Counter(q.reason for q in quarantined)
    payload = {
        "migration_summary": {
            "source_file": source_file,
            "target_database": db_path,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "dry_run": dry_run,
            "transaction_status": "dry_run" if dry_run else "committed",
        },
        "row_counts": {
            "source": source_counts,
            "imported": imported_counts,
            "mismatches": mismatch_details,
        },
        "quarantine_summary": {
            "total_quarantined": len(quarantined),
            "by_reason": dict(q_counter),
        },
        "validation_errors": [
            {
                "entity": i.entity,
                "record_id": i.record_id,
                "field_path": i.field_path,
                "message": i.message,
            }
            for i in validation_issues
        ],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def write_quarantine_artifact(path: Path, quarantined: list[QuarantineRecord]) -> None:
    if not quarantined:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "entity": q.entity,
            "id": q.record_id,
            "reason": q.reason,
            "field": q.field,
            "referenced_id": q.referenced_id,
            "source_data": q.source_data,
        }
        for q in quarantined
    ]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_parity_dump_artifact(path: Path, parity_dump: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(parity_dump, indent=2, ensure_ascii=False), encoding="utf-8")


def write_parity_diff_markdown(
    path: Path,
    source_payload: dict[str, Any],
    parity_dump: dict[str, Any] | None,
    dry_run: bool,
) -> str:
    if dry_run or parity_dump is None:
        content = "# Migration Parity Diff\n\nDry run mode was used. SQLite parity diff was not generated because no database writes were performed.\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return content

    source_canon = _canonicalize(source_payload)
    parity_canon = _canonicalize(parity_dump)
    diff = DeepDiff(source_canon, parity_canon, ignore_order=True, verbose_level=2)

    lines = ["# Migration Parity Diff", "", "## Summary"]
    if not diff:
        lines.append("No differences detected after canonical comparison.")
    else:
        lines.append(f"Differences detected in {len(diff.keys())} section(s).")
        lines.append("")
        lines.append("## DeepDiff")
        lines.append("```json")
        lines.append(diff.to_json(indent=2, ensure_ascii=False))
        lines.append("```")

    content = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return content


def write_migration_report_markdown(
    path: Path,
    counts_payload: dict[str, Any],
    validation_issues: list[ValidationIssue],
    quarantined: list[QuarantineRecord],
    sample_checks: dict[str, Any] | None,
    dry_run: bool,
) -> str:
    lines = ["# Migration Report", ""]
    lines.append("## Run Mode")
    lines.append("DRY RUN - no database writes were performed." if dry_run else "WRITE MODE - transaction committed.")
    lines.append("")

    lines.append("## Row Counts")
    lines.append("```json")
    lines.append(json.dumps(counts_payload.get("row_counts", {}), indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")

    lines.append("## Validation Failures")
    if not validation_issues:
        lines.append("No validation failures.")
    else:
        for issue in validation_issues:
            lines.append(
                f"- entity={issue.entity} id={issue.record_id} field={issue.field_path} message={issue.message}"
            )
    lines.append("")

    lines.append("## Quarantine")
    if not quarantined:
        lines.append("No quarantined records.")
    else:
        for q in quarantined:
            lines.append(
                f"- entity={q.entity} id={q.record_id} reason={q.reason} field={q.field} referenced_id={q.referenced_id}"
            )
    lines.append("")

    lines.append("## Spot Checks")
    if not sample_checks:
        lines.append("Spot checks unavailable in dry-run mode.")
    else:
        lines.append("```json")
        lines.append(json.dumps(sample_checks, indent=2, ensure_ascii=False))
        lines.append("```")

    content = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return content

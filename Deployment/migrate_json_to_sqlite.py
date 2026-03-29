from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text

# Ensure project root is importable when script is launched from Deployment/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import SessionLocal, init_db  # noqa: E402
from backend.models import (  # noqa: E402
    ActivityLog,
    CashTransaction,
    Category,
    Debtor,
    Order,
    OrderItem,
    PasswordRequirement,
    Product,
    ProductSize,
    StoreSettings,
    StoreUser,
)
from backend.paths import get_sqlite_db_path  # noqa: E402
from Deployment.backend.migration import (  # noqa: E402
    build_parity_dump,
    build_sample_checks,
    import_payload,
    load_source_payload,
    validate_and_prepare,
    write_counts_artifact,
    write_migration_report_markdown,
    write_parity_diff_markdown,
    write_parity_dump_artifact,
    write_quarantine_artifact,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="One-time JSON to SQLite migration")
    parser.add_argument(
        "--source",
        default=str(PROJECT_ROOT / "data" / "db.json"),
        help="Path to source JSON file (default: data/db.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report only, without writing to SQLite",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow migration into a non-empty database",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(PROJECT_ROOT / "artifacts"),
        help="Directory for generated migration artifacts",
    )
    return parser.parse_args()


def _database_is_non_empty(db) -> bool:
    tables = [
        Category,
        StoreUser,
        Product,
        ProductSize,
        Order,
        OrderItem,
        CashTransaction,
        ActivityLog,
        Debtor,
        StoreSettings,
        PasswordRequirement,
    ]
    return any(db.query(model).first() is not None for model in tables)


def _counts_mismatch_exists(source_counts: dict[str, int], imported_counts: dict[str, int]) -> bool:
    for key, source_count in source_counts.items():
        if imported_counts.get(key, 0) != source_count:
            return True
    return False


def _reset_existing_data(db) -> None:
    # Delete children first to satisfy FK constraints while preserving schema.
    db.query(PasswordRequirement).delete()
    db.query(OrderItem).delete()
    db.query(CashTransaction).delete()
    db.query(ActivityLog).delete()
    db.query(ProductSize).delete()
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(StoreUser).delete()
    db.query(Debtor).delete()
    db.query(StoreSettings).delete()


def run() -> int:
    args = parse_args()

    source_path = Path(args.source)
    artifacts_dir = Path(args.artifacts_dir)
    counts_path = artifacts_dir / "migration_counts.json"
    quarantine_path = artifacts_dir / "migration_quarantine.json"
    parity_dump_path = artifacts_dir / "migration_parity_dump.json"

    migration_report_path = PROJECT_ROOT / "Documentation" / "Migration_Report.md"
    parity_diff_path = PROJECT_ROOT / "Documentation" / "Migration_Parity_Diff.md"

    loaded = load_source_payload(source_path, artifacts_dir)
    validation_result = validate_and_prepare(loaded.payload)

    if validation_result.has_hard_failures:
        counts_payload = write_counts_artifact(
            path=counts_path,
            source_counts=validation_result.prepared.source_counts,
            imported_counts={key: 0 for key in validation_result.prepared.source_counts},
            quarantined=[],
            validation_issues=validation_result.issues,
            dry_run=args.dry_run,
            source_file=str(loaded.copied_source_path),
            db_path=get_sqlite_db_path(),
        )
        write_migration_report_markdown(
            path=migration_report_path,
            counts_payload=counts_payload,
            validation_issues=validation_result.issues,
            quarantined=[],
            sample_checks=None,
            dry_run=args.dry_run,
        )
        write_parity_diff_markdown(
            path=parity_diff_path,
            source_payload=loaded.payload,
            parity_dump=None,
            dry_run=True,
        )
        print("Migration aborted due to validation errors. Check artifacts and report files.")
        return 1

    init_db()

    parity_dump: dict[str, Any] | None = None
    sample_checks: dict[str, Any] | None = None

    db = SessionLocal()
    try:
        non_empty_db = _database_is_non_empty(db)
        if not args.dry_run and non_empty_db and not args.overwrite:
            print("Refusing to run against non-empty database. Use --overwrite to proceed.")
            return 1

        if args.dry_run:
            import_result = import_payload(db=None, prepared=validation_result.prepared, dry_run=True)
        else:
            # End any implicit transaction opened during preflight read checks.
            db.rollback()
            with db.begin():
                if non_empty_db and args.overwrite:
                    _reset_existing_data(db)
                import_result = import_payload(db=db, prepared=validation_result.prepared, dry_run=False)

            integrity_check_result = db.execute(text("PRAGMA integrity_check;")).scalar()
            if integrity_check_result != "ok":
                print(f"Migration failed integrity_check: {integrity_check_result}")
                return 1
            print(f"Post-import integrity_check: {integrity_check_result}")

            parity_dump = build_parity_dump(db)
            sample_checks = build_sample_checks(db)

    except Exception as exc:
        db.rollback()
        print(f"Migration failed and was rolled back: {exc}")
        return 1
    finally:
        db.close()

    write_quarantine_artifact(quarantine_path, import_result.quarantined)

    if parity_dump is not None:
        write_parity_dump_artifact(parity_dump_path, parity_dump)

    counts_payload = write_counts_artifact(
        path=counts_path,
        source_counts=validation_result.prepared.source_counts,
        imported_counts=import_result.imported_counts,
        quarantined=import_result.quarantined,
        validation_issues=validation_result.issues,
        dry_run=args.dry_run,
        source_file=str(loaded.copied_source_path),
        db_path=get_sqlite_db_path(),
    )

    write_parity_diff_markdown(
        path=parity_diff_path,
        source_payload=loaded.payload,
        parity_dump=parity_dump,
        dry_run=args.dry_run,
    )

    write_migration_report_markdown(
        path=migration_report_path,
        counts_payload=counts_payload,
        validation_issues=validation_result.issues,
        quarantined=import_result.quarantined,
        sample_checks=sample_checks,
        dry_run=args.dry_run,
    )

    if _counts_mismatch_exists(
        source_counts=validation_result.prepared.source_counts,
        imported_counts=import_result.imported_counts,
    ):
        print("Migration completed with mismatches. See reports for quarantine/validation details.")
    else:
        print("Migration completed successfully with full count parity.")

    print(
        "Alembic handoff: stamp this migrated database once with "
        "'alembic -c Deployment/backend/alembic.ini stamp 0001_initial_schema' "
        "using the correct MERBANA_DB_URL."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())

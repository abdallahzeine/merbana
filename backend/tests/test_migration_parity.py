import json
from pathlib import Path

from sqlalchemy import text


ROOT = Path(__file__).resolve().parents[2]
COUNTS_PATH = ROOT / "artifacts" / "migration_counts.json"
QUARANTINE_PATH = ROOT / "artifacts" / "migration_quarantine.json"


EXPECTED_COUNT_KEYS = {
    "store_settings",
    "password_requirements",
    "categories",
    "users",
    "products",
    "product_sizes",
    "orders",
    "order_items",
    "cash_transactions",
    "activity_log",
    "debtors",
}


def test_artifact_row_counts_have_expected_shape():
    payload = json.loads(COUNTS_PATH.read_text(encoding="utf-8"))

    source = payload["row_counts"]["source"]
    imported = payload["row_counts"]["imported"]

    assert set(source.keys()) == EXPECTED_COUNT_KEYS
    assert set(imported.keys()) == EXPECTED_COUNT_KEYS


def test_artifact_row_counts_match_except_quarantine_allowance():
    payload = json.loads(COUNTS_PATH.read_text(encoding="utf-8"))
    source = payload["row_counts"]["source"]
    imported = payload["row_counts"]["imported"]

    quarantined = 0
    if QUARANTINE_PATH.exists():
        quarantined_payload = json.loads(QUARANTINE_PATH.read_text(encoding="utf-8"))
        quarantined = len(quarantined_payload)

    total_source = sum(source.values())
    total_imported = sum(imported.values())

    assert total_imported <= total_source
    assert (total_source - total_imported) <= quarantined


def test_integrity_check_returns_ok(test_engine):
    with test_engine.connect() as conn:
        result = conn.execute(text("PRAGMA integrity_check")).scalar()

    assert result == "ok"

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "merbana.db"
DEFAULT_JSON_OUTPUT = PROJECT_ROOT / "artifacts" / "performance_query_plans.json"
DEFAULT_MD_OUTPUT = PROJECT_ROOT / "Documentation" / "Performance_Query_Plans.md"


@dataclass(frozen=True)
class QuerySpec:
    key: str
    description: str
    sql: str
    params: tuple


def _collect_reference_values(conn: sqlite3.Connection) -> dict:
    values: dict[str, str | int | None] = {}

    row = conn.execute("SELECT MIN(date), MAX(date) FROM orders").fetchone()
    if row and row[0] and row[1]:
        values["orders_min_date"] = row[0]
        values["orders_max_date"] = row[1]
    else:
        now = datetime.now(timezone.utc)
        values["orders_min_date"] = now.isoformat().replace("+00:00", "Z")
        values["orders_max_date"] = (now + timedelta(days=1)).isoformat().replace("+00:00", "Z")

    row = conn.execute("SELECT order_number FROM orders ORDER BY order_number DESC LIMIT 1").fetchone()
    values["sample_order_number"] = int(row[0]) if row else 1

    row = conn.execute("SELECT category_id FROM products WHERE category_id IS NOT NULL LIMIT 1").fetchone()
    values["sample_category_id"] = row[0] if row else None

    row = conn.execute("SELECT name FROM products LIMIT 1").fetchone()
    if row and row[0]:
        values["sample_product_search"] = str(row[0]).split()[0]
    else:
        values["sample_product_search"] = "Product"

    row = conn.execute("SELECT user_id FROM activity_log WHERE user_id IS NOT NULL LIMIT 1").fetchone()
    values["sample_user_id"] = row[0] if row else None

    return values


def _build_queries(ref: dict) -> list[QuerySpec]:
    min_date = ref["orders_min_date"]
    max_date = ref["orders_max_date"]
    sample_order = f"%{ref['sample_order_number']}%"
    sample_product_search = f"%{ref['sample_product_search']}%"
    sample_category_id = ref["sample_category_id"]
    sample_user_id = ref["sample_user_id"]

    return [
        QuerySpec(
            key="orders_date_range_desc",
            description="Orders filtered by date range and sorted descending",
            sql="""
                SELECT id, date, total
                FROM orders
                WHERE date >= ? AND date <= ?
                ORDER BY date DESC
                LIMIT 100
            """,
            params=(min_date, max_date),
        ),
        QuerySpec(
            key="orders_search_order_number",
            description="Orders search by order number text pattern",
            sql="""
                SELECT id, order_number, date
                FROM orders
                WHERE CAST(order_number AS TEXT) LIKE ?
                ORDER BY date DESC
                LIMIT 100
            """,
            params=(sample_order,),
        ),
        QuerySpec(
            key="products_search_name_category",
            description="Product search by name wildcard and category filter",
            sql="""
                SELECT id, name, category_id
                FROM products
                WHERE name LIKE ? AND (? IS NULL OR category_id = ?)
                ORDER BY name
                LIMIT 100
            """,
            params=(sample_product_search, sample_category_id, sample_category_id),
        ),
        QuerySpec(
            key="debtors_unpaid",
            description="Debtors unpaid filter sorted by created_at desc",
            sql="""
                SELECT id, created_at
                FROM debtors
                WHERE paid_at IS NULL
                ORDER BY created_at DESC
                LIMIT 100
            """,
            params=(),
        ),
        QuerySpec(
            key="debtors_paid",
            description="Debtors paid filter sorted by created_at desc",
            sql="""
                SELECT id, created_at
                FROM debtors
                WHERE paid_at IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 100
            """,
            params=(),
        ),
        QuerySpec(
            key="activity_user_date_range",
            description="Activity logs filtered by user and date range",
            sql="""
                SELECT id, timestamp
                FROM activity_log
                WHERE (? IS NULL OR user_id = ?) AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
                LIMIT 100
            """,
            params=(sample_user_id, sample_user_id, min_date, max_date),
        ),
        QuerySpec(
            key="register_balance_python_equivalent",
            description="Register balance source scan used by current service path",
            sql="""
                SELECT type, amount
                FROM cash_transactions
            """,
            params=(),
        ),
        QuerySpec(
            key="register_balance_sql_aggregate_candidate",
            description="Register balance SQL aggregate candidate for future optimization",
            sql="""
                SELECT
                    COALESCE(SUM(CASE WHEN type IN ('sale', 'deposit') THEN amount ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN type IN ('withdrawal', 'shift_close') THEN amount ELSE 0 END), 0)
                FROM cash_transactions
            """,
            params=(),
        ),
        QuerySpec(
            key="reports_daily_breakdown_server_candidate",
            description="Server-side daily breakdown candidate replacing client aggregation",
            sql="""
                SELECT substr(date, 1, 10) AS day, COUNT(*) AS orders_count, SUM(total) AS revenue
                FROM orders
                WHERE date >= ? AND date <= ?
                GROUP BY day
                ORDER BY day ASC
            """,
            params=(min_date, max_date),
        ),
    ]


def _explain(conn: sqlite3.Connection, spec: QuerySpec) -> list[str]:
    explain_rows = conn.execute(f"EXPLAIN QUERY PLAN {spec.sql}", spec.params).fetchall()
    return [str(row[3]) for row in explain_rows]


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def _write_markdown(path: Path, payload: dict) -> None:
    lines = []
    lines.append("# Performance Query Plans")
    lines.append("")
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- Generated at: {payload['generated_at']}")
    lines.append(f"- Database path: {payload['database_path']}")
    lines.append(f"- SQLite journal mode: {payload['journal_mode']}")
    lines.append("")
    lines.append("## Query Plan Evidence")
    lines.append("")
    lines.append("| Query Key | Description | Plan Details |")
    lines.append("|---|---|---|")

    for entry in payload["plans"]:
        details = "<br>".join(_md_escape(line) for line in entry["plan_details"])
        lines.append(
            f"| {_md_escape(entry['key'])} | {_md_escape(entry['description'])} | {details or 'No details'} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is observational for Task 8 and is not a release gate by default.")
    lines.append("- Any FULL SCAN entries should be reviewed as optimization candidates in follow-up tasks.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate EXPLAIN QUERY PLAN evidence report")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH, help="SQLite database path")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUTPUT, help="JSON output path")
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUTPUT, help="Markdown report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    conn = sqlite3.connect(str(args.db_path))
    try:
        ref = _collect_reference_values(conn)
        plans = []
        for query in _build_queries(ref):
            plans.append(
                {
                    "key": query.key,
                    "description": query.description,
                    "sql": " ".join(query.sql.split()),
                    "params": list(query.params),
                    "plan_details": _explain(conn, query),
                }
            )

        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        payload = {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "database_path": str(args.db_path),
            "journal_mode": journal_mode,
            "plans": plans,
        }

        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _write_markdown(args.md_out, payload)

        print("Query plan report generated")
        print(f"JSON: {args.json_out}")
        print(f"Markdown: {args.md_out}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

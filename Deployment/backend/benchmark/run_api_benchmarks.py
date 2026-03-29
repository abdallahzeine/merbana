from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Callable

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_SOURCE_PATH = PROJECT_ROOT / "artifacts" / "benchmark_source_dataset.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "artifacts" / "performance_api_benchmark.json"
DEFAULT_DOC_PATH = PROJECT_ROOT / "Documentation" / "Performance_Baseline.md"


def _get_app_factory() -> Callable[[], object]:
    from backend.app import create_app

    return create_app


def _get_db_path() -> str:
    from backend.paths import get_sqlite_db_path

    return get_sqlite_db_path()


@dataclass(frozen=True)
class Scenario:
    key: str
    method: str
    path: str
    payload_factory: Callable[[], dict | None]
    expected_status: set[int]


def _percentile(values_ms: list[float], p: float) -> float:
    if not values_ms:
        return 0.0
    ordered = sorted(values_ms)
    rank = (p / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    if low == high:
        return round(ordered[low], 3)
    fraction = rank - low
    return round(ordered[low] + (ordered[high] - ordered[low]) * fraction, 3)


def _measure_request(client: TestClient, scenario: Scenario) -> float:
    payload = scenario.payload_factory()
    start = time.perf_counter()
    if scenario.method == "GET":
        response = client.get(scenario.path)
    elif scenario.method == "POST":
        response = client.post(scenario.path, json=payload)
    else:
        raise ValueError(f"Unsupported method: {scenario.method}")
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    if response.status_code not in scenario.expected_status:
        raise RuntimeError(
            f"Scenario {scenario.key} failed with {response.status_code}: {response.text}"
        )

    return elapsed_ms


def _ensure_dataset_exists(source_path: Path) -> None:
    if source_path.exists():
        return
    cmd = [
        sys.executable,
        "Deployment/backend/benchmark/generate_dataset.py",
        "--source-out",
        str(source_path),
    ]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate dataset: {result.stderr or result.stdout}")


def _run_migration(source_path: Path) -> dict:
    cmd = [
        sys.executable,
        "Deployment/migrate_json_to_sqlite.py",
        "--source",
        str(source_path),
        "--overwrite",
    ]
    start = time.perf_counter()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)

    return {
        "duration_ms": round(elapsed_ms, 3),
        "command": " ".join(cmd),
        "stdout_tail": (result.stdout or "")[-1200:],
    }


def _load_reference_data() -> dict:
    import sqlite3

    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        order_row = conn.execute(
            "SELECT id, date FROM orders ORDER BY date DESC LIMIT 1"
        ).fetchone()
        category_row = conn.execute(
            "SELECT category_id FROM products WHERE category_id IS NOT NULL LIMIT 1"
        ).fetchone()
        product_row = conn.execute("SELECT id, name, price FROM products LIMIT 1").fetchone()
        date_bounds = conn.execute("SELECT MIN(date), MAX(date) FROM orders").fetchone()

        if not order_row or not product_row or not date_bounds:
            raise RuntimeError("Benchmark DB does not contain required seed data")

        return {
            "order_id": order_row[0],
            "date_from": date_bounds[0],
            "date_to": date_bounds[1],
            "category_id": category_row[0] if category_row else None,
            "search_term": str(product_row[1]).split()[0],
            "product_id": product_row[0],
            "product_name": product_row[1],
            "product_price": float(product_row[2]),
        }
    finally:
        conn.close()


def _build_scenarios(ref: dict) -> list[Scenario]:
    note_suffix = int(time.time())

    def create_order_payload() -> dict:
        return {
            "payment_method": "cash",
            "order_type": "takeaway",
            "note": f"benchmark-order-{note_suffix}-{int(time.time() * 1000)}",
            "items": [
                {
                    "product_id": ref["product_id"],
                    "name": ref["product_name"],
                    "price": ref["product_price"],
                    "quantity": 1,
                    "size": None,
                    "subtotal": ref["product_price"],
                }
            ],
        }

    def deposit_payload() -> dict:
        return {"amount": 5.0, "note": f"benchmark-deposit-{int(time.time() * 1000)}"}

    def withdrawal_payload() -> dict:
        return {"amount": 2.0, "note": f"benchmark-withdraw-{int(time.time() * 1000)}"}

    category_part = (
        f"&category_id={ref['category_id']}" if ref.get("category_id") else ""
    )

    return [
        Scenario(
            key="orders_list",
            method="GET",
            path="/api/orders?limit=100&offset=0",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="orders_date_range",
            method="GET",
            path=f"/api/orders?limit=100&offset=0&date_from={ref['date_from']}&date_to={ref['date_to']}",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="orders_search_order_number",
            method="GET",
            path="/api/orders?limit=100&offset=0&search=1",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="products_search_filter",
            method="GET",
            path=f"/api/products?search={ref['search_term']}{category_part}",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="dashboard_inputs_register",
            method="GET",
            path="/api/register?limit=50",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="receipt_lookup",
            method="GET",
            path=f"/api/orders/{ref['order_id']}",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="debtors_unpaid",
            method="GET",
            path="/api/debtors?status=unpaid",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="activity_view",
            method="GET",
            path=f"/api/activity?limit=100&date_from={ref['date_from']}&date_to={ref['date_to']}",
            payload_factory=lambda: None,
            expected_status={200},
        ),
        Scenario(
            key="order_create_write",
            method="POST",
            path="/api/orders",
            payload_factory=create_order_payload,
            expected_status={201},
        ),
        Scenario(
            key="register_deposit_write",
            method="POST",
            path="/api/register/deposit",
            payload_factory=deposit_payload,
            expected_status={201},
        ),
        Scenario(
            key="register_withdrawal_write",
            method="POST",
            path="/api/register/withdrawal",
            payload_factory=withdrawal_payload,
            expected_status={201, 422},
        ),
    ]


def _benchmark_scenario(
    app_factory: Callable[[], object], scenario: Scenario, warm_runs: int, cold_runs: int
) -> dict:
    warm_samples: list[float] = []
    cold_samples: list[float] = []

    try:
        app = app_factory()
        with TestClient(app) as client:
            for _ in range(warm_runs):
                warm_samples.append(_measure_request(client, scenario))

        for _ in range(cold_runs):
            app = app_factory()
            with TestClient(app) as cold_client:
                cold_samples.append(_measure_request(cold_client, scenario))
    except Exception as exc:
        return {
            "key": scenario.key,
            "method": scenario.method,
            "path": scenario.path,
            "warm_runs": warm_runs,
            "cold_runs": cold_runs,
            "error": str(exc),
        }

    return {
        "key": scenario.key,
        "method": scenario.method,
        "path": scenario.path,
        "warm_runs": warm_runs,
        "cold_runs": cold_runs,
        "warm": {
            "p50_ms": _percentile(warm_samples, 50),
            "p95_ms": _percentile(warm_samples, 95),
            "mean_ms": round(mean(warm_samples), 3) if warm_samples else 0.0,
        },
        "cold": {
            "p50_ms": _percentile(cold_samples, 50),
            "p95_ms": _percentile(cold_samples, 95),
            "mean_ms": round(mean(cold_samples), 3) if cold_samples else 0.0,
        },
    }


def _write_markdown(path: Path, payload: dict) -> None:
    lines = []
    lines.append("# Performance Baseline")
    lines.append("")
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- Generated at: {payload['generated_at']}")
    lines.append(f"- Database path: {payload['environment']['db_path']}")
    lines.append(f"- Journal mode: {payload['environment']['journal_mode']}")
    lines.append(f"- Dataset source: {payload['dataset_source']}")
    lines.append(f"- Warm runs per scenario: {payload['warm_runs']}")
    lines.append(f"- Cold runs per scenario: {payload['cold_runs']}")
    lines.append("")

    lines.append("## Migration Throughput")
    lines.append("")
    mig = payload["migration"]
    lines.append(f"- Duration: {mig['duration_ms']} ms")
    lines.append(f"- Command: {mig['command']}")
    lines.append("")

    lines.append("## API Latency (p50/p95)")
    lines.append("")
    lines.append("| Scenario | Method | Warm p50 (ms) | Warm p95 (ms) | Cold p50 (ms) | Cold p95 (ms) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for row in payload["results"]:
        if "error" in row:
            lines.append(
                f"| {row['key']} | {row['method']} | n/a | n/a | n/a | n/a |"
            )
            continue

        lines.append(
            f"| {row['key']} | {row['method']} | {row['warm']['p50_ms']} | {row['warm']['p95_ms']} | {row['cold']['p50_ms']} | {row['cold']['p95_ms']} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This baseline is observational and intended for trend tracking.")
    lines.append("- Known heavy paths should be tracked as optimization candidates in follow-up tasks.")
    failed = [row for row in payload["results"] if "error" in row]
    if failed:
        lines.append("- Some scenarios failed during measurement and are listed below.")
        for row in failed:
            lines.append(f"  - {row['key']}: {row['error']}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Task 8 API performance benchmarks")
    parser.add_argument("--source-path", type=Path, default=DEFAULT_SOURCE_PATH, help="Benchmark source dataset JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="JSON results output")
    parser.add_argument("--doc-out", type=Path, default=DEFAULT_DOC_PATH, help="Markdown baseline report output")
    parser.add_argument("--warm-runs", type=int, default=20, help="Warm run iterations per scenario")
    parser.add_argument("--cold-runs", type=int, default=5, help="Cold run iterations per scenario")
    parser.add_argument(
        "--skip-migration",
        action="store_true",
        help="Skip migration refresh before API benchmarks",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    _ensure_dataset_exists(args.source_path)

    migration_result = {
        "duration_ms": 0.0,
        "command": "skipped",
        "stdout_tail": "",
    }
    if not args.skip_migration:
        migration_result = _run_migration(args.source_path)

    ref = _load_reference_data()
    scenarios = _build_scenarios(ref)
    app_factory = _get_app_factory()

    results = []
    for scenario in scenarios:
        results.append(
            _benchmark_scenario(
                app_factory=app_factory,
                scenario=scenario,
                warm_runs=args.warm_runs,
                cold_runs=args.cold_runs,
            )
        )

    import sqlite3

    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    finally:
        conn.close()

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "dataset_source": str(args.source_path),
        "warm_runs": args.warm_runs,
        "cold_runs": args.cold_runs,
        "environment": {
            "db_path": db_path,
            "journal_mode": journal_mode,
            "python": sys.version,
        },
        "migration": migration_result,
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.doc_out, payload)

    print("API benchmarks completed")
    print(f"Results JSON: {args.output}")
    print(f"Baseline doc: {args.doc_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

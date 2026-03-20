from __future__ import annotations

import argparse
import importlib
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_PATH = PROJECT_ROOT / "artifacts" / "benchmark_source_dataset.json"
DEFAULT_MANIFEST_PATH = (
    PROJECT_ROOT / "Deployment" / "backend" / "benchmark" / "benchmark_dataset_manifest.json"
)


@dataclass(frozen=True)
class DatasetConfig:
    products: int = 200
    orders: int = 1000
    activity_log: int = 5000
    register_transactions: int = 1000
    debtors: int = 300
    categories: int = 24
    users: int = 12
    seed: int = 42


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _id(seed: int, entity: str, index: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"benchmark:{seed}:{entity}:{index}"))


def _build_settings() -> dict:
    return {
        "companyName": "Merbana Benchmark Store",
        "security": {
            "passwordRequiredFor": {
                "create_order": False,
                "delete_order": True,
                "deposit_cash": False,
                "withdraw_cash": True,
                "close_shift": True,
                "add_debtor": False,
                "mark_debtor_paid": False,
                "delete_debtor": True,
                "import_database": True,
            }
        },
    }


def generate_payload(config: DatasetConfig) -> dict:
    Faker = importlib.import_module("faker").Faker

    rng = random.Random(config.seed)
    fake = Faker()
    fake.seed_instance(config.seed)

    now = datetime.now(timezone.utc)
    users = []
    categories = []
    products = []
    orders = []
    cash_transactions = []
    activity_log = []
    debtors = []

    for idx in range(config.users):
        users.append(
            {
                "id": _id(config.seed, "user", idx),
                "name": fake.name(),
                "password": None,
                "createdAt": _iso(now - timedelta(days=rng.randint(90, 720))),
            }
        )

    for idx in range(config.categories):
        categories.append(
            {
                "id": _id(config.seed, "category", idx),
                "name": f"Category {idx + 1}",
            }
        )

    size_names = ["Small", "Medium", "Large", "XL"]
    for idx in range(config.products):
        base_price = round(rng.uniform(2.0, 35.0), 2)
        product_sizes = []
        if rng.random() < 0.55:
            for size_idx in range(rng.randint(1, 3)):
                product_sizes.append(
                    {
                        "name": size_names[size_idx],
                        "price": round(base_price + (size_idx * rng.uniform(1.0, 3.0)), 2),
                    }
                )

        products.append(
            {
                "id": _id(config.seed, "product", idx),
                "name": f"{fake.word().title()} {idx + 1}",
                "price": base_price,
                "categoryId": rng.choice(categories)["id"] if rng.random() < 0.9 else None,
                "createdAt": _iso(now - timedelta(days=rng.randint(30, 900))),
                "stock": rng.randint(0, 300),
                "trackStock": rng.random() < 0.8,
                "sizes": product_sizes,
            }
        )

    for idx in range(config.orders):
        order_id = _id(config.seed, "order", idx)
        order_date = now - timedelta(
            days=rng.randint(0, 120),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        items = []
        selected_products = rng.sample(products, k=rng.randint(1, 5))
        order_total = 0.0

        for item_idx, product in enumerate(selected_products):
            quantity = rng.randint(1, 4)
            if product.get("sizes") and rng.random() < 0.4:
                size = rng.choice(product["sizes"])
                unit_price = float(size["price"])
                size_name = str(size["name"])
            else:
                unit_price = float(product["price"])
                size_name = None

            subtotal = round(unit_price * quantity, 2)
            order_total += subtotal

            items.append(
                {
                    "productId": product["id"],
                    "name": product["name"],
                    "price": unit_price,
                    "quantity": quantity,
                    "size": size_name,
                    "subtotal": subtotal,
                }
            )

        order_total = round(order_total, 2)
        order_user = rng.choice(users)
        orders.append(
            {
                "id": order_id,
                "orderNumber": (idx % 100) + 1,
                "date": _iso(order_date),
                "total": order_total,
                "paymentMethod": "cash" if rng.random() < 0.72 else "shamcash",
                "orderType": "dine_in" if rng.random() < 0.6 else "takeaway",
                "note": fake.sentence(nb_words=6) if rng.random() < 0.35 else None,
                "userId": order_user["id"],
                "userName": order_user["name"],
                "items": items,
            }
        )

    tx_types = ["deposit", "withdrawal", "shift_close"]
    running_balance = 0.0

    for idx in range(config.register_transactions):
        tx_id = _id(config.seed, "register_tx", idx)
        tx_date = now - timedelta(
            days=rng.randint(0, 120),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59),
        )

        if idx < min(config.orders, int(config.register_transactions * 0.65)):
            source_order = orders[idx]
            tx_type = "sale"
            amount = float(source_order["total"])
            order_id = source_order["id"]
            tx_user = next((u for u in users if u["id"] == source_order["userId"]), None)
        else:
            tx_type = rng.choice(tx_types)
            amount = round(rng.uniform(5.0, 220.0), 2)
            order_id = None
            tx_user = rng.choice(users)

        if tx_type in ["sale", "deposit"]:
            running_balance += amount
        else:
            running_balance -= amount

        cash_transactions.append(
            {
                "id": tx_id,
                "type": tx_type,
                "amount": amount,
                "note": f"{tx_type} benchmark entry",
                "date": _iso(tx_date),
                "orderId": order_id,
                "userId": tx_user["id"] if tx_user else None,
            }
        )

    action_templates = [
        "Order created",
        "Order deleted",
        "Cash deposited",
        "Cash withdrawn",
        "Shift closed",
        "Product updated",
        "Debtor marked paid",
        "Settings updated",
    ]

    for idx in range(config.activity_log):
        user = rng.choice(users)
        log_date = now - timedelta(
            days=rng.randint(0, 140),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59),
        )
        activity_log.append(
            {
                "id": _id(config.seed, "activity", idx),
                "userId": user["id"] if rng.random() < 0.9 else None,
                "userName": user["name"],
                "action": rng.choice(action_templates),
                "timestamp": _iso(log_date),
            }
        )

    for idx in range(config.debtors):
        created_at = now - timedelta(days=rng.randint(0, 220), hours=rng.randint(0, 23))
        paid = rng.random() < 0.44
        paid_at = _iso(created_at + timedelta(days=rng.randint(1, 45))) if paid else None
        debtors.append(
            {
                "id": _id(config.seed, "debtor", idx),
                "name": fake.name(),
                "amount": round(rng.uniform(8.0, 500.0), 2),
                "note": fake.sentence(nb_words=5) if rng.random() < 0.4 else None,
                "createdAt": _iso(created_at),
                "paidAt": paid_at,
            }
        )

    payload = {
        "products": products,
        "categories": categories,
        "orders": orders,
        "register": {
            "currentBalance": round(running_balance, 2),
            "transactions": cash_transactions,
        },
        "users": users,
        "activityLog": activity_log,
        "settings": _build_settings(),
        "debtors": debtors,
        "lastStockReset": _iso(now - timedelta(days=1)),
    }

    return payload


def _build_manifest(config: DatasetConfig, source_path: Path) -> dict:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "source_dataset": str(source_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "seed": config.seed,
        "dataset": {
            "products": config.products,
            "orders": config.orders,
            "activity_log": config.activity_log,
            "register_transactions": config.register_transactions,
            "debtors": config.debtors,
            "categories": config.categories,
            "users": config.users,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic benchmark dataset")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--source-out", type=Path, default=DEFAULT_SOURCE_PATH, help="Output source JSON path")
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Benchmark manifest JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = DatasetConfig(seed=args.seed)
    payload = generate_payload(config)

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)

    args.source_out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    manifest = _build_manifest(config, args.source_out)
    args.manifest_out.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Benchmark dataset generated")
    print(f"Source: {args.source_out}")
    print(f"Manifest: {args.manifest_out}")
    print(f"Counts: {json.dumps(asdict(config), ensure_ascii=False)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from backend.models import (
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

from .validators import PreparedPayload


@dataclass
class QuarantineRecord:
    entity: str
    record_id: str | None
    reason: str
    field: str
    referenced_id: str | None
    source_data: dict[str, Any]


@dataclass
class ImportResult:
    imported_counts: dict[str, int]
    quarantined: list[QuarantineRecord] = field(default_factory=list)


def _q(
    quarantined: list[QuarantineRecord],
    entity: str,
    record: dict[str, Any],
    reason: str,
    field: str,
    referenced_id: str | None,
) -> None:
    quarantined.append(
        QuarantineRecord(
            entity=entity,
            record_id=record.get("id"),
            reason=reason,
            field=field,
            referenced_id=referenced_id,
            source_data=record,
        )
    )


def import_payload(db: Session | None, prepared: PreparedPayload, dry_run: bool) -> ImportResult:
    quarantined: list[QuarantineRecord] = []
    imported_counts = {
        "store_settings": 0,
        "password_requirements": 0,
        "categories": 0,
        "users": 0,
        "products": 0,
        "product_sizes": 0,
        "orders": 0,
        "order_items": 0,
        "cash_transactions": 0,
        "activity_log": 0,
        "debtors": 0,
    }

    category_ids: set[str] = set()
    user_ids: set[str] = set()
    product_ids: set[str] = set()
    order_ids: set[str] = set()

    if prepared.settings:
        imported_counts["store_settings"] = 1
        imported_counts["password_requirements"] = len(prepared.password_requirements)
        if not dry_run and db is not None:
            settings_obj = StoreSettings(
                id=1,
                company_name=prepared.settings["company_name"],
                last_stock_reset=prepared.last_stock_reset,
            )
            db.add(settings_obj)
            for action_name, is_required in prepared.password_requirements.items():
                db.add(
                    PasswordRequirement(
                        store_settings_id=1,
                        action_name=action_name,
                        is_required=is_required,
                    )
                )

    for rec in prepared.categories:
        imported_counts["categories"] += 1
        category_ids.add(rec["id"])
        if not dry_run and db is not None:
            db.add(Category(**rec))

    for rec in prepared.users:
        imported_counts["users"] += 1
        user_ids.add(rec["id"])
        if not dry_run and db is not None:
            db.add(StoreUser(**rec))

    for rec in prepared.products:
        category_id = rec.get("category_id")
        if category_id and category_id not in category_ids:
            _q(
                quarantined,
                "products",
                rec,
                "foreign_key_violation",
                "category_id",
                category_id,
            )
            continue

        imported_counts["products"] += 1
        product_ids.add(rec["id"])
        if not dry_run and db is not None:
            db.add(Product(**rec))

    for rec in prepared.product_sizes:
        product_id = rec.get("product_id")
        if product_id not in product_ids:
            _q(
                quarantined,
                "product_sizes",
                rec,
                "foreign_key_violation",
                "product_id",
                product_id,
            )
            continue

        imported_counts["product_sizes"] += 1
        if not dry_run and db is not None:
            db.add(ProductSize(**rec))

    skipped_order_ids: set[str] = set()
    for rec in prepared.orders:
        user_id = rec.get("user_id")
        if user_id and user_id not in user_ids:
            _q(
                quarantined,
                "orders",
                rec,
                "foreign_key_violation",
                "user_id",
                user_id,
            )
            skipped_order_ids.add(rec["id"])
            continue

        imported_counts["orders"] += 1
        order_ids.add(rec["id"])
        if not dry_run and db is not None:
            db.add(Order(**rec))

    for rec in prepared.order_items:
        order_id = rec.get("order_id")
        if order_id in skipped_order_ids or order_id not in order_ids:
            _q(
                quarantined,
                "order_items",
                rec,
                "foreign_key_violation",
                "order_id",
                order_id,
            )
            continue
        product_id = rec.get("product_id")
        if product_id and product_id not in product_ids:
            _q(
                quarantined,
                "order_items",
                rec,
                "foreign_key_violation",
                "product_id",
                product_id,
            )
            continue

        imported_counts["order_items"] += 1
        if not dry_run and db is not None:
            db.add(OrderItem(**rec))

    for rec in prepared.cash_transactions:
        order_id = rec.get("order_id")
        user_id = rec.get("user_id")
        if order_id and order_id not in order_ids:
            _q(
                quarantined,
                "cash_transactions",
                rec,
                "foreign_key_violation",
                "order_id",
                order_id,
            )
            continue
        if user_id and user_id not in user_ids:
            _q(
                quarantined,
                "cash_transactions",
                rec,
                "foreign_key_violation",
                "user_id",
                user_id,
            )
            continue

        imported_counts["cash_transactions"] += 1
        if not dry_run and db is not None:
            db.add(CashTransaction(**rec))

    for rec in prepared.activity_logs:
        user_id = rec.get("user_id")
        if user_id and user_id not in user_ids:
            _q(
                quarantined,
                "activity_log",
                rec,
                "foreign_key_violation",
                "user_id",
                user_id,
            )
            continue

        imported_counts["activity_log"] += 1
        if not dry_run and db is not None:
            db.add(ActivityLog(**rec))

    for rec in prepared.debtors:
        imported_counts["debtors"] += 1
        if not dry_run and db is not None:
            db.add(Debtor(**rec))

    return ImportResult(imported_counts=imported_counts, quarantined=quarantined)

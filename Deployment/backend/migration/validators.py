from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.schemas import (
    ActivityLogCreate,
    CashTransactionCreate,
    CategoryCreate,
    DebtorResponse,
    PaymentMethod,
    OrderType,
    ProductCreate,
    ProductSizeCreate,
    SettingsCreate,
    UserCreate,
)
from backend.schemas.common import TimestampStr, UUIDstr


class MigrationOrderItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: UUIDstr | None = None
    name: str = Field(max_length=255)
    price: float = Field(ge=0)
    quantity: int = Field(gt=0)
    size: str | None = Field(default=None, max_length=100)
    subtotal: float = Field(ge=0)


class MigrationOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUIDstr
    order_number: int
    date: TimestampStr
    total: float = Field(ge=0)
    payment_method: PaymentMethod
    order_type: OrderType
    note: str | None = None
    user_id: UUIDstr | None = None
    user_name: str | None = Field(default=None, max_length=255)
    items: list[MigrationOrderItem] = Field(default_factory=list, min_length=1)


@dataclass
class ValidationIssue:
    entity: str
    record_id: str | None
    field_path: str
    message: str


@dataclass
class PreparedPayload:
    categories: list[dict[str, Any]] = field(default_factory=list)
    users: list[dict[str, Any]] = field(default_factory=list)
    products: list[dict[str, Any]] = field(default_factory=list)
    product_sizes: list[dict[str, Any]] = field(default_factory=list)
    orders: list[dict[str, Any]] = field(default_factory=list)
    order_items: list[dict[str, Any]] = field(default_factory=list)
    cash_transactions: list[dict[str, Any]] = field(default_factory=list)
    activity_logs: list[dict[str, Any]] = field(default_factory=list)
    debtors: list[dict[str, Any]] = field(default_factory=list)
    settings: dict[str, Any] | None = None
    password_requirements: dict[str, bool] = field(default_factory=dict)
    last_stock_reset: str | None = None
    source_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class ValidationResult:
    prepared: PreparedPayload
    issues: list[ValidationIssue]
    has_hard_failures: bool


def _camel_to_snake_record(raw: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    out = dict(raw)
    for old_key, new_key in mapping.items():
        if old_key in out:
            out[new_key] = out.pop(old_key)
    return out


def _append_pydantic_error(
    issues: list[ValidationIssue],
    entity: str,
    record_id: str | None,
    err: ValidationError,
) -> None:
    for e in err.errors():
        loc = ".".join(str(x) for x in e.get("loc", []))
        issues.append(
            ValidationIssue(
                entity=entity,
                record_id=record_id,
                field_path=loc or "<root>",
                message=e.get("msg", "Validation error"),
            )
        )


def _check_duplicate_ids(
    issues: list[ValidationIssue], entity: str, records: list[dict[str, Any]]
) -> None:
    seen: set[str] = set()
    for rec in records:
        rid = rec.get("id")
        if not rid:
            continue
        if rid in seen:
            issues.append(
                ValidationIssue(
                    entity=entity,
                    record_id=rid,
                    field_path="id",
                    message="Duplicate ID detected in source payload",
                )
            )
            return
        seen.add(rid)


def validate_and_prepare(payload: dict[str, Any]) -> ValidationResult:
    issues: list[ValidationIssue] = []
    prepared = PreparedPayload()

    required_top_keys = [
        "products",
        "categories",
        "orders",
        "register",
        "users",
        "activityLog",
        "settings",
        "debtors",
    ]
    for key in required_top_keys:
        if key not in payload:
            issues.append(
                ValidationIssue(
                    entity="root",
                    record_id=None,
                    field_path=key,
                    message="Missing required top-level key",
                )
            )

    categories_raw = payload.get("categories", []) or []
    users_raw = payload.get("users", []) or []
    products_raw = payload.get("products", []) or []
    orders_raw = payload.get("orders", []) or []
    register_raw = payload.get("register", {}) or {}
    tx_raw = register_raw.get("transactions", []) or []
    activity_raw = payload.get("activityLog", []) or []
    debtors_raw = payload.get("debtors", []) or []
    settings_raw = payload.get("settings", {}) or {}

    # Categories
    for raw in categories_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("categories", None, "<root>", "Record must be an object"))
            continue
        try:
            rec = CategoryCreate.model_validate(raw)
            prepared.categories.append(rec.model_dump())
        except ValidationError as err:
            _append_pydantic_error(issues, "categories", raw.get("id"), err)

    # Users
    for raw in users_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("users", None, "<root>", "Record must be an object"))
            continue
        normalized = _camel_to_snake_record(raw, {"createdAt": "created_at"})
        try:
            rec = UserCreate.model_validate(normalized)
            prepared.users.append(rec.model_dump())
        except ValidationError as err:
            _append_pydantic_error(issues, "users", raw.get("id"), err)

    # Products + Product Sizes
    for raw in products_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("products", None, "<root>", "Record must be an object"))
            continue
        normalized = _camel_to_snake_record(
            raw,
            {
                "createdAt": "created_at",
                "categoryId": "category_id",
                "trackStock": "track_stock",
            },
        )
        sizes_raw = normalized.get("sizes") or []
        normalized_sizes: list[dict[str, Any]] = []
        for index, size in enumerate(sizes_raw):
            if not isinstance(size, dict):
                issues.append(
                    ValidationIssue(
                        "product_sizes",
                        normalized.get("id"),
                        f"sizes.{index}",
                        "Size record must be an object",
                    )
                )
                continue
            size_payload = {
                "id": str(uuid5(NAMESPACE_URL, f"{normalized.get('id', 'missing')}:size:{index}")),
                "sort_order": index,
                "name": size.get("name"),
                "price": size.get("price"),
            }
            try:
                size_rec = ProductSizeCreate.model_validate(size_payload)
                normalized_sizes.append(size_rec.model_dump())
            except ValidationError as err:
                _append_pydantic_error(
                    issues,
                    "product_sizes",
                    normalized.get("id"),
                    err,
                )

        normalized["sizes"] = normalized_sizes
        try:
            rec = ProductCreate.model_validate(normalized)
            product_dump = rec.model_dump(exclude={"sizes"})
            prepared.products.append(product_dump)
            for size in rec.sizes:
                size_dump = size.model_dump()
                size_dump["product_id"] = rec.id
                prepared.product_sizes.append(size_dump)
        except ValidationError as err:
            _append_pydantic_error(issues, "products", raw.get("id"), err)

    # Orders + Order items
    for raw in orders_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("orders", None, "<root>", "Record must be an object"))
            continue
        normalized = _camel_to_snake_record(
            raw,
            {
                "orderNumber": "order_number",
                "paymentMethod": "payment_method",
                "orderType": "order_type",
                "userId": "user_id",
                "userName": "user_name",
            },
        )
        items_raw = normalized.get("items") or []
        normalized_items: list[dict[str, Any]] = []
        for index, item in enumerate(items_raw):
            if not isinstance(item, dict):
                issues.append(
                    ValidationIssue(
                        "order_items",
                        normalized.get("id"),
                        f"items.{index}",
                        "Order item record must be an object",
                    )
                )
                continue
            normalized_item = _camel_to_snake_record(item, {"productId": "product_id"})
            try:
                item_rec = MigrationOrderItem.model_validate(normalized_item)
                normalized_items.append(item_rec.model_dump())
            except ValidationError as err:
                _append_pydantic_error(issues, "order_items", normalized.get("id"), err)

        normalized["items"] = normalized_items
        try:
            order_rec = MigrationOrder.model_validate(normalized)
            order_dump = {
                "id": order_rec.id,
                "order_number": order_rec.order_number,
                "date": order_rec.date,
                "total": order_rec.total,
                "payment_method": order_rec.payment_method.value,
                "order_type": order_rec.order_type.value,
                "note": order_rec.note,
                "user_id": order_rec.user_id,
                "user_name": order_rec.user_name,
            }
            prepared.orders.append(order_dump)
            for index, item in enumerate(order_rec.items):
                item_dump = item.model_dump()
                item_dump["id"] = str(
                    uuid5(NAMESPACE_URL, f"{order_rec.id}:item:{index}")
                )
                item_dump["order_id"] = order_rec.id
                prepared.order_items.append(item_dump)
        except ValidationError as err:
            _append_pydantic_error(issues, "orders", raw.get("id"), err)

    # Register transactions
    for raw in tx_raw:
        if not isinstance(raw, dict):
            issues.append(
                ValidationIssue("cash_transactions", None, "<root>", "Record must be an object")
            )
            continue
        normalized = _camel_to_snake_record(raw, {"orderId": "order_id", "userId": "user_id"})
        try:
            rec = CashTransactionCreate.model_validate(normalized)
            prepared.cash_transactions.append(rec.model_dump())
        except ValidationError as err:
            _append_pydantic_error(issues, "cash_transactions", raw.get("id"), err)

    # Activity logs
    for raw in activity_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("activity_log", None, "<root>", "Record must be an object"))
            continue
        normalized = _camel_to_snake_record(raw, {"userId": "user_id", "userName": "user_name"})
        try:
            rec = ActivityLogCreate.model_validate(normalized)
            prepared.activity_logs.append(rec.model_dump())
        except ValidationError as err:
            _append_pydantic_error(issues, "activity_log", raw.get("id"), err)

    # Debtors
    for raw in debtors_raw:
        if not isinstance(raw, dict):
            issues.append(ValidationIssue("debtors", None, "<root>", "Record must be an object"))
            continue
        normalized = _camel_to_snake_record(raw, {"createdAt": "created_at", "paidAt": "paid_at"})
        try:
            rec = DebtorResponse.model_validate(normalized)
            prepared.debtors.append(rec.model_dump())
        except ValidationError as err:
            _append_pydantic_error(issues, "debtors", raw.get("id"), err)

    # Settings + password requirements map
    settings_payload = {
        "company_name": settings_raw.get("companyName", ""),
        "security": settings_raw.get("security", {}),
    }
    settings_for_schema = {
        "company_name": settings_payload["company_name"],
        "security": settings_payload["security"],
    }
    if "passwordRequiredFor" in settings_for_schema.get("security", {}):
        settings_for_schema["security"] = {
            "password_required_for": settings_for_schema["security"].get("passwordRequiredFor")
        }

    try:
        rec = SettingsCreate.model_validate(settings_for_schema)
        prepared.settings = {"company_name": rec.company_name}
        prepared.password_requirements = rec.security.password_required_for.model_dump()
    except ValidationError as err:
        _append_pydantic_error(issues, "settings", "1", err)

    last_stock_reset = payload.get("lastStockReset")
    if last_stock_reset is not None and not isinstance(last_stock_reset, str):
        issues.append(
            ValidationIssue(
                entity="settings",
                record_id="1",
                field_path="lastStockReset",
                message="lastStockReset must be a string when provided",
            )
        )
    prepared.last_stock_reset = last_stock_reset if isinstance(last_stock_reset, str) else None

    # Duplicate ID checks (fail-fast classes)
    _check_duplicate_ids(issues, "categories", prepared.categories)
    _check_duplicate_ids(issues, "users", prepared.users)
    _check_duplicate_ids(issues, "products", prepared.products)
    _check_duplicate_ids(issues, "product_sizes", prepared.product_sizes)
    _check_duplicate_ids(issues, "orders", prepared.orders)
    _check_duplicate_ids(issues, "order_items", prepared.order_items)
    _check_duplicate_ids(issues, "cash_transactions", prepared.cash_transactions)
    _check_duplicate_ids(issues, "activity_log", prepared.activity_logs)
    _check_duplicate_ids(issues, "debtors", prepared.debtors)

    prepared.source_counts = {
        "store_settings": 1 if prepared.settings else 0,
        "password_requirements": len(prepared.password_requirements),
        "categories": len(categories_raw),
        "users": len(users_raw),
        "products": len(products_raw),
        "product_sizes": sum(len((p or {}).get("sizes", []) or []) for p in products_raw if isinstance(p, dict)),
        "orders": len(orders_raw),
        "order_items": sum(len((o or {}).get("items", []) or []) for o in orders_raw if isinstance(o, dict)),
        "cash_transactions": len(tx_raw),
        "activity_log": len(activity_raw),
        "debtors": len(debtors_raw),
    }

    has_hard_failures = len(issues) > 0

    return ValidationResult(prepared=prepared, issues=issues, has_hard_failures=has_hard_failures)

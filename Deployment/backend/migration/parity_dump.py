from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.models import (
    ActivityLog,
    CashTransaction,
    Category,
    Debtor,
    Order,
    Product,
    StoreSettings,
    StoreUser,
)


def _balance_from_transactions(transactions: list[CashTransaction]) -> float:
    balance = 0.0
    for tx in transactions:
        if tx.type in {"sale", "deposit"}:
            balance += tx.amount
        elif tx.type in {"withdrawal", "shift_close"}:
            balance -= tx.amount
    return balance


def _with_optional(target: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        target[key] = value


def build_parity_dump(db: Session) -> dict[str, Any]:
    categories = db.query(Category).order_by(Category.id).all()
    products = db.query(Product).order_by(Product.id).all()
    orders = db.query(Order).order_by(Order.id).all()
    transactions = db.query(CashTransaction).order_by(CashTransaction.id).all()
    users = db.query(StoreUser).order_by(StoreUser.id).all()
    activities = db.query(ActivityLog).order_by(ActivityLog.id).all()
    debtors = db.query(Debtor).order_by(Debtor.id).all()
    settings = db.query(StoreSettings).first()

    settings_payload: dict[str, Any] = {
        "companyName": settings.company_name if settings else "",
        "security": {"passwordRequiredFor": {}},
    }

    if settings:
        for req in sorted(settings.password_requirements, key=lambda r: r.action_name):
            settings_payload["security"]["passwordRequiredFor"][req.action_name] = req.is_required

    products_payload: list[dict[str, Any]] = []
    for p in products:
        record = {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "createdAt": p.created_at,
        }
        _with_optional(record, "categoryId", p.category_id)
        _with_optional(record, "trackStock", p.track_stock)
        _with_optional(record, "stock", p.stock)
        if p.sizes:
            record["sizes"] = [{"name": s.name, "price": s.price} for s in p.sizes]
        products_payload.append(record)

    orders_payload: list[dict[str, Any]] = []
    for o in orders:
        record = {
            "id": o.id,
            "orderNumber": o.order_number,
            "date": o.date,
            "total": o.total,
            "paymentMethod": o.payment_method,
            "orderType": o.order_type,
            "items": [],
        }
        _with_optional(record, "note", o.note)
        _with_optional(record, "userId", o.user_id)
        _with_optional(record, "userName", o.user_name)
        record["items"] = [
            {
                **({"productId": i.product_id} if i.product_id else {}),
                "name": i.name,
                "price": i.price,
                "quantity": i.quantity,
                **({"size": i.size} if i.size else {}),
                "subtotal": i.subtotal,
            }
            for i in sorted(o.items, key=lambda item: item.id)
        ]
        orders_payload.append(record)

    tx_payload = []
    for t in transactions:
        record = {
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "date": t.date,
        }
        _with_optional(record, "note", t.note)
        _with_optional(record, "orderId", t.order_id)
        _with_optional(record, "userId", t.user_id)
        tx_payload.append(record)

    activity_payload = []
    for a in activities:
        record = {
            "id": a.id,
            "userName": a.user_name,
            "action": a.action,
            "timestamp": a.timestamp,
        }
        _with_optional(record, "userId", a.user_id)
        activity_payload.append(record)

    debtors_payload = []
    for d in debtors:
        record = {
            "id": d.id,
            "name": d.name,
            "amount": d.amount,
            "createdAt": d.created_at,
        }
        _with_optional(record, "note", d.note)
        _with_optional(record, "paidAt", d.paid_at)
        debtors_payload.append(record)

    return {
        "products": products_payload,
        "categories": [{"id": c.id, "name": c.name} for c in categories],
        "orders": orders_payload,
        "register": {
            "currentBalance": _balance_from_transactions(transactions),
            "transactions": tx_payload,
        },
        "users": [
            {
                **({"password": u.password} if u.password else {}),
                "id": u.id,
                "name": u.name,
                "createdAt": u.created_at,
            }
            for u in users
        ],
        "activityLog": activity_payload,
        "settings": settings_payload,
        "debtors": debtors_payload,
        "lastStockReset": settings.last_stock_reset if settings else None,
    }


def build_sample_checks(db: Session) -> dict[str, Any]:
    first_order = db.query(Order).order_by(Order.date.asc(), Order.id.asc()).first()
    first_tx = db.query(CashTransaction).order_by(CashTransaction.date.asc(), CashTransaction.id.asc()).first()

    return {
        "category": _as_dict(db.query(Category).order_by(Category.id.asc()).first()),
        "user": _as_dict(db.query(StoreUser).order_by(StoreUser.id.asc()).first()),
        "product": _as_dict(db.query(Product).order_by(Product.id.asc()).first()),
        "order": _as_dict(first_order),
        "order_item": _as_dict(first_order.items[0]) if first_order and first_order.items else None,
        "cash_transaction": _as_dict(first_tx),
        "activity_log": _as_dict(db.query(ActivityLog).order_by(ActivityLog.id.asc()).first()),
        "debtor": _as_dict(db.query(Debtor).order_by(Debtor.id.asc()).first()),
        "settings": _as_dict(db.query(StoreSettings).first()),
        "order_workflow_chain": {
            "order_id": first_order.id if first_order else None,
            "order_item_count": len(first_order.items) if first_order else 0,
            "sale_transactions_for_order": db.query(CashTransaction)
            .filter(CashTransaction.order_id == first_order.id if first_order else False)
            .count()
            if first_order
            else 0,
        },
    }


def _as_dict(model_obj: Any) -> dict[str, Any] | None:
    if model_obj is None:
        return None
    if not hasattr(model_obj, "__table__"):
        return None
    return {col.name: getattr(model_obj, col.name) for col in model_obj.__table__.columns}

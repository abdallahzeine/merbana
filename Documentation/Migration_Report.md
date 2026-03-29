# Migration Report

## Run Mode
WRITE MODE - transaction committed.

## Row Counts
```json
{
  "source": {
    "store_settings": 1,
    "password_requirements": 9,
    "categories": 24,
    "users": 12,
    "products": 200,
    "product_sizes": 218,
    "orders": 1000,
    "order_items": 3042,
    "cash_transactions": 1000,
    "activity_log": 5000,
    "debtors": 300
  },
  "imported": {
    "store_settings": 1,
    "password_requirements": 9,
    "categories": 24,
    "users": 12,
    "products": 200,
    "product_sizes": 218,
    "orders": 1000,
    "order_items": 3042,
    "cash_transactions": 1000,
    "activity_log": 5000,
    "debtors": 300
  },
  "mismatches": []
}
```

## Validation Failures
No validation failures.

## Quarantine
No quarantined records.

## Spot Checks
```json
{
  "category": {
    "id": "009a8513-7e3b-56a3-a572-58b506913e48",
    "name": "Category 7"
  },
  "user": {
    "id": "0bdf83be-0488-5199-9456-a9668877fb73",
    "name": "Jamie Arnold",
    "password": null,
    "created_at": "2025-11-18T16:45:27Z"
  },
  "product": {
    "id": "00566570-c50b-5e0d-ab7d-9c8693b47b6b",
    "name": "Traditional 121",
    "price": 31.8,
    "category_id": "80d79b6f-a7a1-5119-9d30-bd8b5e49ddf0",
    "created_at": "2025-07-09T16:45:27Z",
    "stock": null,
    "track_stock": null
  },
  "order": {
    "id": "dd62fd46-8d37-5acc-abca-333e7ee70bb1",
    "order_number": 46,
    "date": "2025-11-19T16:49:27Z",
    "total": 75.63,
    "payment_method": "cash",
    "order_type": "dine_in",
    "note": null,
    "user_id": "4b2438c6-943c-52b6-a5e8-c912cd74bf1a",
    "user_name": "Angie Henderson"
  },
  "order_item": {
    "id": "e6404b7f-f6fc-5965-be0e-425f66262f18",
    "order_id": "dd62fd46-8d37-5acc-abca-333e7ee70bb1",
    "product_id": "b473c644-67ce-58a6-8887-59d5897d0dd2",
    "name": "Knowledge 111",
    "price": 15.53,
    "quantity": 3,
    "size": null,
    "subtotal": 46.59
  },
  "cash_transaction": {
    "id": "7ae84a92-4e68-59ff-95d6-ab50766c10e3",
    "type": "shift_close",
    "amount": 153.99,
    "note": "shift_close benchmark entry",
    "date": "2025-11-19T20:01:51Z",
    "order_id": null,
    "user_id": "ec01350e-c787-5c2f-9c2c-a20cdc2dbc31"
  },
  "activity_log": {
    "id": "002ebbba-200f-5377-8b70-7de9e050dfb8",
    "user_id": "0bdf83be-0488-5199-9456-a9668877fb73",
    "user_name": "Jamie Arnold",
    "action": "Settings updated",
    "timestamp": "2026-01-05T09:43:48Z"
  },
  "debtor": {
    "id": "004b4b3c-eaf1-59b2-bf75-1f1fe4074e8b",
    "name": "Marcia Wu",
    "amount": 58.45,
    "note": null,
    "created_at": "2025-08-21T09:45:27Z",
    "paid_at": "2025-09-17T09:45:27Z"
  },
  "settings": {
    "id": 1,
    "company_name": "Merbana Benchmark Store",
    "last_stock_reset": "2026-03-19T16:45:27Z"
  },
  "order_workflow_chain": {
    "order_id": "dd62fd46-8d37-5acc-abca-333e7ee70bb1",
    "order_item_count": 2,
    "sale_transactions_for_order": 1
  }
}
```

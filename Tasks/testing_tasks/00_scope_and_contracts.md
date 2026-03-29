# 00 Scope and Contracts

## Goal
Freeze the implementation scope for high-priority tests T1-T46 and lock contract expectations before coding tests.

## Includes
- Users: T1-T7
- Categories: T11-T14
- Products: T15-T32
- Orders: T33-T44
- Receipt mapping: T45-T46

## Contract Decisions To Lock
- List endpoints may return `data` and optional `total`.
- API field mapping must respect snake_case in transport and camelCase in frontend models.
- Error assertions must include status and response payload snapshot.

## Known Mismatch Log (must decide before test coding)
- Products stock path mismatch (`/products/{id}/stock` vs `/products/{id}/adjust-stock`).
- Orders list payload shape differences (summary vs full object).
- Register mismatches are out of scope for T1-T46 but must remain documented.

## Checklist
- [x] Confirm all T1-T46 IDs and ownership.
- [x] Confirm expected request/response shape by endpoint.
- [x] Confirm mismatch resolution strategy (adapt client, patch backend, or compatibility layer).
- [x] Record locked expectations in this file.

## Locked Ownership (T1-T46)
- Users: T1-T7 (03_users_t1_t7.md)
- Categories: T11-T14 (04_categories_t11_t14.md)
- Products CRUD: T15-T22 (05_products_crud_t15_t22.md)
- Products sizes: T23-T27 (06_products_sizes_t23_t27.md)
- Products stock/workflow: T28-T32 (07_products_stock_t28_t32.md)
- Orders read: T33-T35 (08_orders_read_t33_t35.md)
- Orders create/delete: T36-T44 (09_orders_create_delete_t36_t44.md)
- Receipt mapping: T45-T46 (10_receipt_t45_t46.md)

## Locked Endpoint Contracts (Users/Categories/Products/Orders/Receipt)
- Transport convention: request/response payloads use snake_case. Frontend models use camelCase via schema transforms.
- List endpoints in scope may return `{"data": [...], "total": <number|null>}`; tests assert `data` required and `total` optional/nullable.
- Error assertions for negative paths must assert both HTTP status and full JSON error payload snapshot.

### Users
- `GET /api/users` -> `UserListResponse` shape with `data` array and optional/nullable `total`.
- `POST /api/users` creates user and returns created user (201).
- `PUT /api/users/{id}` updates user and returns updated user (200).
- `DELETE /api/users/{id}` returns 204 with no body.

### Categories
- `GET /api/categories` -> `CategoryListResponse` with category objects including `product_count`.
- `POST /api/categories` creates category (201).
- `DELETE /api/categories/{id}` returns 204 for empty category; guarded delete can return conflict.

### Products
- `GET /api/products` -> `ProductListResponse` (`data`, optional/nullable `total`).
- `GET /api/products/{id}` returns full product with sizes.
- `POST /api/products` creates product (201).
- `PUT /api/products/{id}` updates product.
- `DELETE /api/products/{id}` returns 204.
- Stock adjustment canonical backend endpoint is `POST /api/products/{id}/stock` with `{ "quantity_delta": number }`.

### Orders
- `GET /api/orders/next-number` returns `{ "order_number": number }`.
- `GET /api/orders` returns summary list (`OrderSummaryListResponse`) with `data` entries containing summary fields and `total`.
- `GET /api/orders/{id}` returns full order object with items.
- `POST /api/orders` creates order and returns full order (201).
- `DELETE /api/orders/{id}` returns 204.

### Receipt Mapping (T45-T46)
- Receipt tests consume full order response (`GET /api/orders/{id}` or create response) plus settings data.
- Assertions must include item mapping (name/qty/price/subtotal), optional size/note rendering, totals, and payment/order type variants.

## Mismatch Resolution (Locked)
- Products stock path mismatch: use compatibility strategy during test implementation.
	- Preferred path for backend contract assertions: `/api/products/{id}/stock`.
	- If frontend helper still calls `/adjust-stock`, tests must either call backend path directly or add a temporary compatibility helper for tests.
- Orders list payload mismatch (summary vs full object): lock list tests (T33-T35) to summary contract from `GET /api/orders`, and use `GET /api/orders/{id}` for full-object assertions.
- Register mismatches: remain documented and explicitly out of scope for T1-T46.

## Contract Baseline Status
- Baseline locked on 2026-03-20 for T1-T46 implementation.
- No unresolved critical mismatch remains for Users/Categories/Products/Orders/Receipt within this scope.

## Done Criteria
- A single, unambiguous contract baseline exists for T1-T46.
- No unresolved critical mismatch remains for Users/Categories/Products/Orders/Receipt.

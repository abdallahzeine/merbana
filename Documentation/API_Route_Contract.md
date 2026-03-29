# API Route Contract

## Standard Error Response Format

All error responses follow this JSON structure:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": null
}
```

For validation errors, an additional `validation_errors` array may be included:

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": null,
  "validation_errors": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request data failed validation |
| `NOT_FOUND` | 404 | Requested entity does not exist |
| `CONFLICT` | 409 | Operation conflicts with existing state |
| `DUPLICATE_ID` | 409 | Entity with same ID already exists |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Health

### GET /api/health

Health check endpoint.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/health` |
| Request Schema | None |
| Response Schema | `{"status": "healthy"}` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Users

Base path: `/api/users`

### GET /api/users

List all users.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/users` |
| Request Schema | None |
| Response Schema | `UserListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "user-001",
      "name": "John Doe",
      "password": "hashed_password",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /api/users

Create a new user.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/users` |
| Request Schema | `UserCreate` |
| Response Schema | `UserResponse` |
| Error Codes | `DUPLICATE_ID`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "id": "user-001",
  "name": "John Doe",
  "password": "hashed_password",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "id": "user-001",
  "name": "John Doe",
  "password": "hashed_password",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/users/{user_id}

Get a user by ID.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/users/{user_id}` |
| Request Schema | None |
| Response Schema | `UserResponse` |
| Error Codes | `NOT_FOUND` |
| Side Effects | None |

### PUT /api/users/{user_id}

Update a user.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/users/{user_id}` |
| Request Schema | `UserUpdate` |
| Response Schema | `UserResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "name": "Jane Doe",
  "password": "new_hashed_password"
}
```

### DELETE /api/users/{user_id}

Delete a user.

| Property | Value |
|----------|-------|
| Method | DELETE |
| Path | `/api/users/{user_id}` |
| Request Schema | None |
| Response Schema | None (204 No Content) |
| Error Codes | `NOT_FOUND` |
| Side Effects | Sets `user_id` to NULL in related activity logs, cash transactions, orders |

---

## Categories

Base path: `/api/categories`

### GET /api/categories

List all categories with product counts.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/categories` |
| Request Schema | None |
| Response Schema | `CategoryListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "cat-001",
      "name": "Beverages",
      "product_count": 15
    }
  ]
}
```

### POST /api/categories

Create a new category.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/categories` |
| Request Schema | `CategoryCreate` |
| Response Schema | `CategoryResponse` |
| Error Codes | `DUPLICATE_ID`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "id": "cat-001",
  "name": "Beverages"
}
```

### GET /api/categories/{category_id}

Get a category by ID.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/categories/{category_id}` |
| Request Schema | None |
| Response Schema | `CategoryWithProductCount` |
| Error Codes | `NOT_FOUND` |
| Side Effects | None |

### PUT /api/categories/{category_id}

Update a category.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/categories/{category_id}` |
| Request Schema | `CategoryUpdate` |
| Response Schema | `CategoryResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "name": "Updated Category Name"
}
```

### DELETE /api/categories/{category_id}

Delete a category (guarded).

| Property | Value |
|----------|-------|
| Method | DELETE |
| Path | `/api/categories/{category_id}` |
| Request Schema | None |
| Response Schema | None (204 No Content) |
| Error Codes | `NOT_FOUND`, `CONFLICT` |
| Side Effects | None (prevents deletion if products exist) |

**Error Response (CONFLICT):**
```json
{
  "error": "Cannot delete category 'Beverages': 5 products are assigned to it",
  "code": "CONFLICT",
  "details": null
}
```

---

## Products

Base path: `/api/products`

### GET /api/products

List all products.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/products` |
| Query Parameters | `category_id` (optional), `search` (optional) |
| Request Schema | None |
| Response Schema | `ProductListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "prod-001",
      "name": "Coffee",
      "price": 3.50,
      "category_id": "cat-001",
      "category_name": "Beverages",
      "stock": 100,
      "track_stock": true,
      "created_at": "2024-01-15T10:30:00Z",
      "sizes": [
        {
          "id": "size-001",
          "product_id": "prod-001",
          "name": "Small",
          "price": 0.50,
          "sort_order": 1
        }
      ]
    }
  ]
}
```

### POST /api/products

Create a new product with sizes.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/products` |
| Request Schema | `ProductCreate` |
| Response Schema | `ProductResponse` |
| Error Codes | `DUPLICATE_ID`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "id": "prod-001",
  "name": "Coffee",
  "price": 3.50,
  "category_id": "cat-001",
  "stock": 100,
  "track_stock": true,
  "created_at": "2024-01-15T10:30:00Z",
  "sizes": [
    {
      "id": "size-001",
      "name": "Small",
      "price": 0.50,
      "sort_order": 1
    }
  ]
}
```

### GET /api/products/{product_id}

Get a product by ID.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/products/{product_id}` |
| Request Schema | None |
| Response Schema | `ProductResponse` |
| Error Codes | `NOT_FOUND` |
| Side Effects | None |

### PUT /api/products/{product_id}

Update a product.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/products/{product_id}` |
| Request Schema | `ProductUpdate` |
| Response Schema | `ProductResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | If `sizes` provided, replaces all existing sizes |

**Request:**
```json
{
  "name": "Updated Coffee",
  "price": 4.00,
  "stock": 150,
  "sizes": [
    {
      "id": "size-002",
      "name": "Large",
      "price": 1.00,
      "sort_order": 2
    }
  ]
}
```

### DELETE /api/products/{product_id}

Delete a product.

| Property | Value |
|----------|-------|
| Method | DELETE |
| Path | `/api/products/{product_id}` |
| Request Schema | None |
| Response Schema | None (204 No Content) |
| Error Codes | `NOT_FOUND` |
| Side Effects | Cascades delete all associated sizes |

### POST /api/products/{product_id}/stock

Adjust product stock.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/products/{product_id}/stock` |
| Request Schema | `StockAdjustment` |
| Response Schema | `ProductResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | Updates product stock, logs activity |

**Request:**
```json
{
  "quantity_delta": -5
}
```

### POST /api/products/bulk-stock

Bulk update stock for multiple products.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/products/bulk-stock` |
| Request Schema | `BulkStockUpdate` |
| Response Schema | `List[ProductResponse]` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | Updates stock for all specified products |

**Request:**
```json
{
  "updates": [
    {"product_id": "prod-001", "stock": 100},
    {"product_id": "prod-002", "stock": 50}
  ]
}
```

---

## Orders

Base path: `/api/orders`

### GET /api/orders/next-number

Get the next order number.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/orders/next-number` |
| Request Schema | None |
| Response Schema | `{"order_number": int}` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "order_number": 42
}
```

### GET /api/orders

List orders with filtering and pagination.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/orders` |
| Query Parameters | `date_from`, `date_to`, `search`, `limit`, `offset` |
| Request Schema | None |
| Response Schema | `OrderSummaryListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "ord-001",
      "order_number": 42,
      "date": "2024-01-15T10:30:00Z",
      "total": 15.50
    }
  ],
  "total": 100
}
```

### POST /api/orders

Create a new order.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/orders` |
| Request Schema | `OrderCreate` |
| Response Schema | `OrderResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR`, `INTERNAL_ERROR` |
| Side Effects | Reduces stock, creates cash transaction, logs activity |

**Request:**
```json
{
  "payment_method": "cash",
  "order_type": "dine_in",
  "note": "Extra sugar",
  "user_id": "user-001",
  "user_name": "John Doe",
  "items": [
    {
      "product_id": "prod-001",
      "name": "Coffee",
      "price": 3.50,
      "quantity": 2,
      "size": "Small",
      "subtotal": 7.00
    }
  ]
}
```

**Response:**
```json
{
  "id": "ord-001",
  "order_number": 42,
  "date": "2024-01-15",
  "user_id": "user-001",
  "user_name": "John Doe",
  "total": 7.00,
  "payment_method": "cash",
  "order_type": "dine_in",
  "note": "Extra sugar",
  "items": [...]
}
```

### GET /api/orders/{order_id}

Get an order by ID.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/orders/{order_id}` |
| Request Schema | None |
| Response Schema | `OrderResponse` |
| Error Codes | `NOT_FOUND` |
| Side Effects | None |

### DELETE /api/orders/{order_id}

Delete an order.

| Property | Value |
|----------|-------|
| Method | DELETE |
| Path | `/api/orders/{order_id}` |
| Request Schema | None |
| Response Schema | None (204 No Content) |
| Error Codes | `NOT_FOUND`, `INTERNAL_ERROR` |
| Side Effects | Restores stock, reverses cash transaction, logs activity |

---

## Register

Base path: `/api/register`

### GET /api/register

Get current register state.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/register` |
| Query Parameters | `limit` (default: 50) |
| Request Schema | None |
| Response Schema | `RegisterStateResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "current_balance": 250.75,
  "transactions": [
    {
      "id": "tx-001",
      "type": "deposit",
      "amount": 100.00,
      "date": "2024-01-15T10:30:00Z",
      "user_id": "user-001",
      "user_name": "John Doe",
      "note": "Opening float"
    }
  ]
}
```

### POST /api/register/deposit

Deposit cash into register.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/register/deposit` |
| Request Schema | `DepositRequest` |
| Response Schema | `CashTransactionResponse` |
| Error Codes | `VALIDATION_ERROR`, `INTERNAL_ERROR` |
| Side Effects | Increases register balance, logs activity |

**Request:**
```json
{
  "amount": 50.00,
  "note": "Additional float"
}
```

### POST /api/register/withdrawal

Withdraw cash from register.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/register/withdrawal` |
| Request Schema | `WithdrawalRequest` |
| Response Schema | `CashTransactionResponse` |
| Error Codes | `VALIDATION_ERROR` (insufficient balance), `INTERNAL_ERROR` |
| Side Effects | Decreases register balance, logs activity |

**Request:**
```json
{
  "amount": 25.00,
  "note": "Cash pickup"
}
```

### POST /api/register/close-shift

Close the current shift.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/register/close-shift` |
| Request Schema | `ShiftCloseRequest` |
| Response Schema | `CashTransactionResponse` or `{"message": string, "balance": 0}` |
| Error Codes | `INTERNAL_ERROR` |
| Side Effects | Zeros out register balance, creates shift_close transaction, logs activity |

**Request:**
```json
{
  "note": "End of day"
}
```

### GET /api/register/transactions

List cash transactions.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/register/transactions` |
| Query Parameters | `limit` (default: 100), `offset` (default: 0), `date_from`, `date_to` |
| Request Schema | None |
| Response Schema | `CashTransactionListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "tx-001",
      "type": "sale",
      "amount": 15.50,
      "date": "2024-01-15T10:30:00Z",
      "user_id": "user-001",
      "user_name": "John Doe",
      "note": "Order #42"
    }
  ],
  "total": 150
}
```

---

## Debtors

Base path: `/api/debtors`

### GET /api/debtors

List debtors.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/debtors` |
| Query Parameters | `status` (unpaid|paid|all, default: all) |
| Request Schema | None |
| Response Schema | `DebtorListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "debt-001",
      "name": "Customer Name",
      "amount": 25.50,
      "note": "Tab for lunch",
      "created_at": "2024-01-15T10:30:00Z",
      "paid_at": null
    }
  ]
}
```

### POST /api/debtors

Create a new debtor.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/debtors` |
| Request Schema | `DebtorCreate` |
| Response Schema | `DebtorResponse` |
| Error Codes | `DUPLICATE_ID`, `VALIDATION_ERROR` |
| Side Effects | Logs activity |

**Request:**
```json
{
  "id": "debt-001",
  "name": "Customer Name",
  "amount": 25.50,
  "note": "Tab for lunch",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/debtors/{debtor_id}

Get a debtor by ID.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/debtors/{debtor_id}` |
| Request Schema | None |
| Response Schema | `DebtorResponse` |
| Error Codes | `NOT_FOUND` |
| Side Effects | None |

### PUT /api/debtors/{debtor_id}

Update a debtor.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/debtors/{debtor_id}` |
| Request Schema | `DebtorUpdate` |
| Response Schema | `DebtorResponse` |
| Error Codes | `NOT_FOUND`, `VALIDATION_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "note": "Updated note",
  "paid_at": null
}
```

### POST /api/debtors/{debtor_id}/mark-paid

Mark a debtor as paid.

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/api/debtors/{debtor_id}/mark-paid` |
| Request Schema | `MarkPaidRequest` |
| Response Schema | `DebtorResponse` |
| Error Codes | `NOT_FOUND` |
| Side Effects | Sets `paid_at` timestamp, logs activity |

**Request:**
```json
{
  "paid_at": "2024-01-15T14:00:00Z"
}
```

### DELETE /api/debtors/{debtor_id}

Delete a debtor.

| Property | Value |
|----------|-------|
| Method | DELETE |
| Path | `/api/debtors/{debtor_id}` |
| Request Schema | None |
| Response Schema | None (204 No Content) |
| Error Codes | `NOT_FOUND` |
| Side Effects | Logs deletion activity |

---

## Settings

Base path: `/api/settings`

### GET /api/settings

Get application settings.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/settings` |
| Request Schema | None |
| Response Schema | `SettingsResponse` |
| Error Codes | None |
| Side Effects | Creates default settings if not exist |

**Response:**
```json
{
  "id": "settings-001",
  "company_name": "My Store",
  "last_stock_reset": "2024-01-15T00:00:00Z",
  "security": {
    "password_required_for": {
      "delete_order": true,
      "edit_stock": false,
      "view_reports": false
    }
  }
}
```

### PUT /api/settings

Update application settings.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/settings` |
| Request Schema | `SettingsUpdate` |
| Response Schema | `SettingsResponse` |
| Error Codes | `NOT_FOUND`, `INTERNAL_ERROR` |
| Side Effects | None |

**Request:**
```json
{
  "company_name": "New Store Name",
  "last_stock_reset": "2024-01-16T00:00:00Z"
}
```

### GET /api/settings/password-requirements

Get password requirements map.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/settings/password-requirements` |
| Request Schema | None |
| Response Schema | `PasswordRequirementMap` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "delete_order": true,
  "edit_stock": false,
  "view_reports": false
}
```

### PUT /api/settings/password-requirements/{action}

Update password requirement for a single action.

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | `/api/settings/password-requirements/{action}` |
| Query Parameters | `is_required` (boolean) |
| Request Schema | None |
| Response Schema | `SettingsResponse` |
| Error Codes | `NOT_FOUND`, `INTERNAL_ERROR` |
| Side Effects | None |

---

## Activity

Base path: `/api/activity`

### GET /api/activity

List activity logs with filtering.

| Property | Value |
|----------|-------|
| Method | GET |
| Path | `/api/activity` |
| Query Parameters | `user_id`, `date_from`, `date_to`, `limit` (default: 100), `offset` (default: 0) |
| Request Schema | None |
| Response Schema | `ActivityLogListResponse` |
| Error Codes | None |
| Side Effects | None |

**Response:**
```json
{
  "data": [
    {
      "id": "log-001",
      "user_id": "user-001",
      "user_name": "John Doe",
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "Order #42 created - Total: $15.50"
    }
  ],
  "total": 500
}
```

---

## Schema Definitions

### Common Types

```typescript
type UUIDstr = string;
type TimestampStr = string;
```

### User Schemas

```typescript
interface UserCreate {
  id: string;
  name: string;
  password: string;
  created_at: string;
}

interface UserUpdate {
  name?: string;
  password?: string;
}

interface UserResponse {
  id: string;
  name: string;
  password: string;
  created_at: string;
}

interface UserListResponse {
  data: UserResponse[];
}
```

### Category Schemas

```typescript
interface CategoryCreate {
  id: string;
  name: string;
}

interface CategoryUpdate {
  name?: string;
}

interface CategoryResponse {
  id: string;
  name: string;
}

interface CategoryWithProductCount {
  id: string;
  name: string;
  product_count: number;
}

interface CategoryListResponse {
  data: CategoryWithProductCount[];
}
```

### Product Schemas

```typescript
interface ProductSizeCreate {
  id: string;
  name: string;
  price: number;
  sort_order: number;
}

interface ProductSizeResponse {
  id: string;
  product_id: string;
  name: string;
  price: number;
  sort_order: number;
}

interface ProductCreate {
  id: string;
  name: string;
  price: number;
  category_id?: string;
  stock: number;
  track_stock: boolean;
  created_at: string;
  sizes: ProductSizeCreate[];
}

interface ProductUpdate {
  name?: string;
  price?: number;
  category_id?: string;
  stock?: number;
  track_stock?: boolean;
  sizes?: ProductSizeCreate[];
}

interface ProductResponse {
  id: string;
  name: string;
  price: number;
  category_id?: string;
  category_name?: string;
  stock: number;
  track_stock: boolean;
  created_at: string;
  sizes: ProductSizeResponse[];
}

interface ProductListResponse {
  data: ProductResponse[];
}

interface StockAdjustment {
  quantity_delta: number;
}

interface BulkStockUpdate {
  updates: Array<{
    product_id: string;
    stock: number;
  }>;
}
```

### Order Schemas

```typescript
type PaymentMethod = "cash" | "shamcash";
type OrderType = "dine_in" | "takeaway";

interface OrderItemCreate {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  subtotal: number;
}

interface OrderItemResponse {
  id: string;
  order_id: string;
  product_id?: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  subtotal: number;
}

interface OrderCreate {
  payment_method: PaymentMethod;
  order_type: OrderType;
  note?: string;
  user_id?: string;
  user_name?: string;
  items: OrderItemCreate[];
}

interface OrderUpdate {
  note?: string;
}

interface OrderResponse {
  id: string;
  order_number: number;
  date: string;
  user_id?: string;
  user_name?: string;
  total: number;
  payment_method: PaymentMethod;
  order_type: OrderType;
  note?: string;
  items: OrderItemResponse[];
}

interface OrderSummary {
  id: string;
  order_number: number;
  date: string;
  total: number;
}

interface OrderListResponse {
  data: OrderResponse[];
}

interface OrderSummaryListResponse {
  data: OrderSummary[];
  total: number;
}
```

### Register Schemas

```typescript
type TransactionType = "deposit" | "withdrawal" | "sale" | "sale_reversal" | "shift_close";

interface CashTransactionResponse {
  id: string;
  type: TransactionType;
  amount: number;
  date: string;
  user_id?: string;
  user_name?: string;
  note?: string;
}

interface CashTransactionListResponse {
  data: CashTransactionResponse[];
  total: number;
}

interface DepositRequest {
  amount: number;
  note?: string;
}

interface WithdrawalRequest {
  amount: number;
  note?: string;
}

interface ShiftCloseRequest {
  note?: string;
}

interface RegisterStateResponse {
  current_balance: number;
  transactions: CashTransactionResponse[];
}
```

### Debtor Schemas

```typescript
interface DebtorCreate {
  id: string;
  name: string;
  amount: number;
  note?: string;
  created_at: string;
}

interface DebtorUpdate {
  note?: string;
  paid_at?: string;
}

interface DebtorResponse {
  id: string;
  name: string;
  amount: number;
  note?: string;
  created_at: string;
  paid_at?: string;
}

interface DebtorListResponse {
  data: DebtorResponse[];
}

interface MarkPaidRequest {
  paid_at?: string;
}
```

### Settings Schemas

```typescript
type SensitiveActionKey = "delete_order" | "edit_stock" | "view_reports";

interface PasswordRequirementMap {
  delete_order: boolean;
  edit_stock: boolean;
  view_reports: boolean;
}

interface SecuritySettings {
  password_required_for: PasswordRequirementMap;
}

interface SettingsUpdate {
  company_name?: string;
  last_stock_reset?: string;
}

interface SettingsResponse {
  id: string;
  company_name?: string;
  last_stock_reset?: string;
  security: SecuritySettings;
}
```

### Activity Schemas

```typescript
interface ActivityLogResponse {
  id: string;
  user_id?: string;
  user_name?: string;
  timestamp: string;
  action: string;
}

interface ActivityLogListResponse {
  data: ActivityLogResponse[];
  total: number;
}
```

---

## Notes

1. **Transaction Boundaries**: All write operations (`POST`, `PUT`, `DELETE`) use explicit transaction boundaries with automatic rollback on failure.

2. **Date Format**: All timestamps are ISO 8601 format (e.g., `2024-01-15T10:30:00Z`).

3. **ID Generation**: Frontend generates UUID-style IDs; backend validates uniqueness.

4. **CORS**: API allows requests from `http://localhost:{port}` and `http://127.0.0.1:{port}` where port is the configured server port (default: 8741).

5. **Authentication**: Current implementation does not require authentication. Future versions may add JWT-based auth.

6. **Rate Limiting**: No rate limiting implemented for local desktop application.

7. **Pagination**: Endpoints with `limit`/`offset` parameters return a `total` count in the response for pagination UI.
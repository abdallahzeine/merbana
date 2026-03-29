# Frontend API Testing Plan

## Overview

**Goal:** Test all 31 API functions assuming a running backend at `http://localhost:8741`. Cover full CRUD lifecycle for each entity following the workflow: Users → Categories → Products → Orders → Debtors → Register → Reports → Settings.

**Total Tests:** 73
**Total API Functions:** 31 across 8 entity types

---

## Test Configuration

- **Backend URL:** `http://127.0.0.1:8741` (via Vite proxy to `/api`)
- **API Prefix:** `/api`
- **Auth:** User-based (no tokens), users selected from list + optional password
- **No Data Cleanup:** Tests leave data for manual verification
- **Test User:** Tests run as `test-user-{timestamp}`

---

## Test File Structure

```
src/
├── api/
│   └── __tests__/
│       ├── usersApi.test.ts           # T1-T7
│       ├── categoriesApi.test.ts      # T11-T14
│       ├── productsApi.test.ts        # T15-T32
│       ├── ordersApi.test.ts          # T33-T44
│       ├── receiptData.test.ts        # T45-T46
│       ├── debtorsApi.test.ts        # T47-T54
│       ├── registerApi.test.ts        # T55-T62
│       ├── activityApi.test.ts        # T63-T65
│       ├── reportCalculations.test.ts  # T66-T69
│       └── settingsApi.test.ts        # T70-T72
└── integration/
    └── __tests__/
        └── fullWorkflow.test.ts       # T73
```

---

## Phase 1: Users & Authentication (T1-T7)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchUsers` | GET | `/users` | none | `Promise<UserList>` |
| `createUser` | POST | `/users` | `{ id, name, password?, createdAt }` | `Promise<User>` |
| `updateUser` | POST | `/users/{id}` | `id: string, data: { name?, password? }` | `Promise<User>` |
| `deleteUser` | DELETE | `/users/{id}` | `id: string` | `Promise<void>` |

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T1 | Create user without password | `createUser` | `{ id: 'test-1', name: 'Test Cashier', createdAt: '2024-01-01T00:00:00Z' }` | User created with `hasPassword: false` |
| T2 | Create user with password | `createUser` | `{ id: 'test-2', name: 'Test Admin', password: 'secret', createdAt: '2024-01-01T00:00:00Z' }` | User created with `hasPassword: true` |
| T3 | Fetch all users | `fetchUsers` | none | Response has `{ data: User[], total?: number }` |
| T4 | Verify user in list | `fetchUsers` | after T1 | Created user appears in `data` array |
| T5 | Update user name | `updateUser` | `id: 'test-1', { name: 'Updated Name' }` | User name changed |
| T6 | Update user password | `updateUser` | `id: 'test-1', { password: 'newpass' }` | User has new password |
| T7 | Delete user | `deleteUser` | `id: 'test-1'` | User deleted, returns void |

### Test Data Pattern

```typescript
const testUser = {
  id: `test-user-${Date.now()}`,
  name: `Test Cashier ${Date.now()}`,
  createdAt: new Date().toISOString(),
};
```

---

## Phase 2a: Categories API (T11-T14)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchCategories` | GET | `/categories` | none | `Promise<CategoryList>` |
| `createCategory` | POST | `/categories` | `id: string, name: string` | `Promise<Category>` |
| `deleteCategory` | DELETE | `/categories/{id}` | `id: string` | `Promise<void>` |

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T11 | Fetch all categories | `fetchCategories` | none | Returns array of categories |
| T12 | Create beverage category | `createCategory` | `id: 'cat-bev-{ts}', name: 'Beverages'` | Category created |
| T13 | Create food category | `createCategory` | `id: 'cat-food-{ts}', name: 'Food'` | Category created |
| T14 | Delete empty category | `deleteCategory` | `id: 'cat-bev-{ts}'` | Category deleted |

---

## Phase 2b: Products API - Basic CRUD (T15-T22)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchProducts` | GET | `/products` | none | `Promise<ProductList>` |
| `fetchProduct` | GET | `/products/{id}` | `id: string` | `Promise<Product>` |
| `createProduct` | POST | `/products` | `data: Product` | `Promise<Product>` |
| `updateProduct` | POST | `/products/{id}` | `id: string, data: Partial<Product>` | `Promise<Product>` |
| `deleteProduct` | DELETE | `/products/{id}` | `id: string` | `Promise<void>` |
| `adjustStock` | POST | `/products/{productId}/adjust-stock` | `productId: string, quantityDelta: number` | `Promise<Product>` |

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T15 | Create simple product | `createProduct` | `{ id: 'prod-coffee', name: 'Coffee', price: 5.99, categoryId: catId, stock: 100, trackStock: true, createdAt: ts }` | Product created, no sizes |
| T16 | Fetch all products | `fetchProducts` | none | Response has `{ data: Product[] }` |
| T17 | Fetch single product | `fetchProduct` | `id: 'prod-coffee'` | Returns product with all fields |
| T18 | Update product name | `updateProduct` | `id: 'prod-coffee', { name: 'Espresso' }` | Name updated to 'Espresso' |
| T19 | Update product price | `updateProduct` | `id: 'prod-coffee', { price: 6.99 }` | Price updated to 6.99 |
| T20 | Increase stock | `adjustStock` | `id: 'prod-coffee', quantityDelta: 50` | Stock increased by 50 |
| T21 | Decrease stock | `adjustStock` | `id: 'prod-coffee', quantityDelta: -10` | Stock decreased by 10 |
| T22 | Delete product | `deleteProduct` | `id: 'prod-coffee'` | Product deleted |

---

## Phase 2c: Products API - Sizes/Options (T23-T27)

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T23 | Create product with sizes | `createProduct` | Product with `sizes: [{ id, name: 'Small', price: 4.99, sortOrder: 0 }, { id, name: 'Large', price: 6.99, sortOrder: 1 }]` | Product created with 2 sizes |
| T24 | Verify sizes returned | `fetchProduct` | `id: product-with-sizes-id` | `sizes` array has 2 items with correct `name`, `price`, `sortOrder` |
| T25 | Add size to product | `updateProduct` | `id: prodId, { sizes: [...existing, newSize] }` | New size added |
| T26 | Remove size from product | `updateProduct` | `id: prodId, { sizes: [size1, size2] }` where size2 removed | Size array has 1 item |
| T27 | Update size price | `updateProduct` | `id: prodId, { sizes: [{ id, name: 'Small', price: 5.99, sortOrder: 0 }] }` | Size price updated |

### Size Data Structure

```typescript
interface ProductSize {
  id: string;
  name: string;      // e.g., "Small", "Medium", "Large"
  price: number;      // e.g., 4.99
  sortOrder: number;  // e.g., 0
}
```

---

## Phase 2d: Products API - Stock Management (T28-T31)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `bulkSetStock` | POST | `/products/bulk-stock` | `updates: { productId: string; quantityDelta: number }[]` | `Promise<void>` |

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T28 | Create product with stock tracking | `createProduct` | `{ trackStock: true, stock: 50 }` | Product has `trackStock: true` |
| T29 | Verify stock increase | `adjustStock` | `productId, quantityDelta: 100` | New stock = old + 100 |
| T30 | Verify stock decrease | `adjustStock` | `productId, quantityDelta: -30` | New stock = old - 30 |
| T31 | Bulk stock update | `bulkSetStock` | `{ updates: [{ productId: p1, quantityDelta: 10 }, { productId: p2, quantityDelta: -5 }] }` | Both products updated |

---

## Phase 2e: Product Workflow Integration (T32)

| ID | Test | Description |
|----|------|-------------|
| T32 | Full product workflow | 1. Create category "Desserts"<br>2. Create 5 products with sizes<br>3. `fetchProducts` - verify all 5 exist<br>4. `updateProduct` - change prices on 3 products<br>5. `adjustStock` - update stock on 2 products<br>6. Verify all changes persist |

---

## Phase 3a: Orders API - Reading (T33-T35)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `getNextOrderNumber` | GET | `/orders/next-number` | none | `Promise<{ order_number: number }>` |
| `fetchOrders` | GET | `/orders` | `limit = 100, offset = 0` | `Promise<OrderList>` |
| `fetchOrder` | GET | `/orders/{id}` | `id: string` | `Promise<Order>` |

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T33 | Get next order number | `getNextOrderNumber` | none | Returns `{ order_number: number }` |
| T34 | Fetch orders with pagination | `fetchOrders` | `limit: 20, offset: 0` | Returns `{ data: Order[], total?: number }` |
| T35 | Fetch single order | `fetchOrder` | `id: orderId` | Returns order with all fields |

---

## Phase 3b: Orders API - Creating (T36-T42)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `createOrder` | POST | `/orders` | `{ items, paymentMethod, orderType, note?, userId?, userName? }` | `Promise<Order>` |
| `deleteOrder` | DELETE | `/orders/{id}` | `id: string` | `Promise<void>` |

### Order Data Structure

```typescript
interface OrderItem {
  productId?: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  subtotal: number;
}

interface Order {
  id: string;
  orderNumber: number;
  date: string;
  items: OrderItem[];
  total: number;
  paymentMethod: 'cash' | 'shamcash';
  orderType: 'dine_in' | 'takeaway';
  note?: string;
  userId?: string;
  userName?: string;
}
```

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T36 | Create order - cash, dine_in | `createOrder` | `{ items: [item1], paymentMethod: 'cash', orderType: 'dine_in' }` | Order created with status 'completed' |
| T37 | Create order - shamcash | `createOrder` | `{ items: [item1], paymentMethod: 'shamcash', orderType: 'dine_in' }` | Order created with shamcash |
| T38 | Create order - takeaway | `createOrder` | `{ items: [item1], paymentMethod: 'cash', orderType: 'takeaway' }` | Order created with takeaway type |
| T39 | Create order - multiple items | `createOrder` | `{ items: [item1, item2, item3], ... }` | Order has 3 items, total = sum of subtotals |
| T40 | Create order - with sizes | `createOrder` | Items include `size: 'Large'` | Item has size field |
| T41 | Create order - with note | `createOrder` | `{ ..., note: 'Extra napkins please' }` | Order has note field |
| T42 | Verify order data | `fetchOrder` | After T36 | All fields match what was sent |

### Order Item Example

```typescript
const orderItem = {
  productId: 'prod-coffee',
  name: 'Coffee',
  price: 5.99,
  quantity: 2,
  size: 'Large',
  subtotal: 11.98,  // price * quantity
};
```

---

## Phase 3c: Orders API - Deletion & Verification (T43-T44)

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T43 | Delete order | `deleteOrder` | `id: orderId` | Order deleted, returns void |
| T44 | Full order verification | fetch then verify | After creating order | `orderNumber` correct<br>`date` set<br>`items` count matches<br>`total` = sum of item subtotals<br>`paymentMethod` matches<br>`orderType` matches<br>`note` matches if provided |

---

## Phase 3d: Receipt Data Tests (T45-T46)

### Receipt Data Structure Requirements

```typescript
interface ReceiptData {
  companyName: string;       // From settings
  orderNumber: number;       // Padded with zeros (e.g., "00001")
  date: string;              // Formatted Arabic date
  paymentMethod: string;     // "cash" or "shamcash"
  orderType: string;         // "dine_in" or "takeaway"
  items: {
    name: string;
    size?: string;
    quantity: number;
    price: number;
    subtotal: number;
  }[];
  note?: string;
  total: number;
  footer: string;             // From settings
}
```

### Test Cases

| ID | Test | Description |
|----|------|-------------|
| T45 | Receipt data structure | 1. Create order with known data<br>2. Fetch order<br>3. Map order to receipt format<br>4. Verify: companyName (from settings), orderNumber, date, items table, totals, payment method |
| T46 | Receipt with all variations | Create order with: multiple items, sizes, notes, cash payment |

---

## Phase 4: Debtors API (T47-T54)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchDebtors` | GET | `/debtors` | none | `Promise<DebtorList>` |
| `createDebtor` | POST | `/debtors` | `{ id, name, amount, note?, createdAt }` | `Promise<Debtor>` |
| `markDebtorPaid` | POST | `/debtors/{id}/mark-paid` | `id: string, paidAt?: string` | `Promise<Debtor>` |
| `deleteDebtor` | DELETE | `/debtors/{id}` | `id: string` | `Promise<void>` |

### Debtor Data Structure

```typescript
interface Debtor {
  id: string;
  name: string;
  amount: number;
  note?: string;
  createdAt: string;
  paidAt?: string;  // null when unpaid, set when marked paid
}
```

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T47 | Fetch all debtors | `fetchDebtors` | none | Returns `{ data: Debtor[] }` |
| T48 | Create debtor | `createDebtor` | `{ id: 'deb-1', name: 'John Doe', amount: 100.00, createdAt: ts }` | Debtor created with `paidAt: null` |
| T49 | Create debtor with note | `createDebtor` | `{ ..., note: 'Owes for catering' }` | Debtor has note field |
| T50 | Verify debtor in list | `fetchDebtors` | after T48 | Debtor appears in list |
| T51 | Mark debtor paid | `markDebtorPaid` | `id: 'deb-1', paidAt: '2024-01-15T00:00:00Z'` | `paidAt` field is set |
| T52 | Verify paidAt set | `fetchDebtors` | after T51 | Debtor has `paidAt` date |
| T53 | Delete debtor | `deleteDebtor` | `id: 'deb-1'` | Debtor deleted |

### Debtor Workflow Integration (T54)

| ID | Test | Description |
|----|------|-------------|
| T54 | Full debtor workflow | 1. Create 3 debtors (A, B, C)<br>2. `fetchDebtors` - verify all 3 exist<br>3. Mark debtor B as paid<br>4. `fetchDebtors` - verify B has `paidAt`, A and C have `paidAt: null`<br>5. Delete debtors A and C |

---

## Phase 5: Register API (T55-T62)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchRegister` | GET | `/register` | none | `Promise<RegisterState>` |
| `depositCash` | POST | `/register/deposit` | `amount: number, note?: string` | `Promise<CashTransaction>` |
| `withdrawCash` | POST | `/register/withdraw` | `amount: number, note?: string` | `Promise<CashTransaction>` |
| `closeShift` | POST | `/register/close-shift` | `taken: number, note?: string` | `Promise<RegisterState>` |

### Register Data Structure

```typescript
interface CashTransaction {
  id: string;
  type: 'sale' | 'deposit' | 'withdrawal' | 'shift_close';
  amount: number;
  note?: string;
  date: string;
  orderId?: string;
  userId?: string;
}

interface RegisterState {
  currentBalance: number;
  transactions: CashTransaction[];
}
```

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T55 | Get register state | `fetchRegister` | none | Returns `{ currentBalance, transactions[] }` |
| T56 | Deposit cash | `depositCash` | `{ amount: 1000, note: 'Opening float' }` | Transaction created with type 'deposit' |
| T57 | Verify balance after deposit | `fetchRegister` | after T56 | `currentBalance` increased by 1000 |
| T58 | Withdraw cash | `withdrawCash` | `{ amount: 500, note: 'Bank run' }` | Transaction created with type 'withdrawal' |
| T59 | Verify balance after withdrawal | `fetchRegister` | after T58 | `currentBalance` decreased by 500 |
| T60 | Close shift | `closeShift` | `{ taken: 1500, note: 'End of day' }` | Transaction with type 'shift_close', balance resets |

### Transaction History Verification (T61-T62)

| ID | Test | Description |
|----|------|-------------|
| T61 | Verify closed state | After T60, `fetchRegister` shows `currentBalance: 0` |
| T62 | Transaction history | 1. `fetchRegister`<br>2. Verify transactions array contains all: deposit, withdrawal, shift_close<br>3. Each transaction has correct `type`, `amount`, `note`, `date` |

---

## Phase 6: Activity & Reports (T63-T69)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchActivityLog` | GET | `/activity` | none | `Promise<ActivityLogList>` |
| `logActivity` | POST | `/activity` | `userId: string, userName: string, action: string` | `Promise<void>` |

### Activity Data Structure

```typescript
interface ActivityLog {
  id: string;
  userId: string;
  userName: string;
  action: string;  // e.g., "create_order", "login", "logout"
  timestamp: string;
}
```

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T63 | Fetch activity logs | `fetchActivityLog` | none | Returns `{ data: ActivityLog[] }` |
| T64 | Log custom activity | `logActivity` | `'user-1', 'Test User', 'test_action'` | Activity logged |
| T65 | Verify activity appears | `fetchActivityLog` | after T64 | New activity entry exists |

### Report Calculations (T66-T69)

| ID | Test | Description |
|----|------|-------------|
| T66 | Revenue calculation | 1. Create 5 orders with amounts: 10, 20, 30, 40, 50<br>2. Calculate expected: total=150, count=5, avg=30<br>3. `fetchOrders` or use utility functions<br>4. Verify totals match |
| T67 | Payment method breakdown | Create orders with known cash/shamcash distribution<br>Verify breakdown counts are correct |
| T68 | Order type breakdown | Create orders with known dine_in/takeaway distribution<br>Verify breakdown counts are correct |
| T69 | Best selling product | Create orders with products: A(5x), B(3x), C(2x)<br>Verify best selling is A with quantity 5 |

---

## Phase 7: Settings API (T70-T72)

### API Functions Tested

| Function | HTTP | Endpoint | Parameters | Returns |
|---------|------|----------|------------|---------|
| `fetchSettings` | GET | `/settings` | none | `Promise<Settings>` |
| `updateSettings` | POST | `/settings` | `{ companyName?, security? }` | `Promise<Settings>` |

### Settings Data Structure

```typescript
interface SecuritySettings {
  passwordRequiredFor: {
    create_order: boolean;
    delete_order: boolean;
    deposit_cash: boolean;
    withdraw_cash: boolean;
    close_shift: boolean;
    add_debtor: boolean;
    mark_debtor_paid: boolean;
    delete_debtor: boolean;
    import_database: boolean;
  };
}

interface Settings {
  id: string;
  companyName: string;
  lastStockReset?: string;
  security: SecuritySettings;
}
```

### Test Cases

| ID | Test | Function | Input | Expected Result |
|----|------|----------|-------|-----------------|
| T70 | Fetch settings | `fetchSettings` | none | Returns Settings object with companyName, security |
| T71 | Update company name | `updateSettings` | `{ companyName: 'New Restaurant' }` | Settings updated |
| T72 | Update password policy | `updateSettings` | `{ security: { passwordRequiredFor: { delete_order: false } } }` | Policy updated |

---

## Phase 8: Full Integration Test (T73)

### Complete POS Workflow Test

| ID | Test | Description |
|----|------|-------------|
| T73 | Full workflow | 1. **User**: Create user "Test Cashier"<br>2. **Category**: Create "Hot Drinks" category<br>3. **Products**: Create "Coffee" (Small: 4, Large: 6), "Tea" (2.5), "Sandwich" (8)<br>4. **Orders**: Create 3 orders with different payment methods<br>5. **Receipts**: Verify receipt data matches orders<br>6. **Debtors**: Create debtor "John" (50), mark paid<br>7. **Register**: Deposit 1000, withdraw 200, close shift<br>8. **Reports**: Verify all data aggregated correctly<br>9. **Settings**: Update company name<br>10. **Activity**: Verify all actions logged |

---

## Implementation Order

| Order | Phase | Tests | Priority |
|-------|-------|-------|----------|
| 1 | Users API | T1-T7 | HIGH |
| 2 | Categories API | T11-T14 | HIGH |
| 3 | Products - Basic CRUD | T15-T22 | HIGH |
| 4 | Products - Sizes | T23-T27 | HIGH |
| 5 | Products - Stock | T28-T31 | MEDIUM |
| 6 | Products - Integration | T32 | MEDIUM |
| 7 | Orders - Read | T33-T35 | HIGH |
| 8 | Orders - Create | T36-T42 | HIGH |
| 9 | Orders - Delete & Verify | T43-T44 | HIGH |
| 10 | Receipt Data | T45-T46 | HIGH |
| 11 | Debtors | T47-T54 | MEDIUM |
| 12 | Register | T55-T62 | MEDIUM |
| 13 | Activity & Reports | T63-T69 | LOW |
| 14 | Settings | T70-T72 | LOW |
| 15 | Full Integration | T73 | MEDIUM |

---

## Data Verification Checklist

### Product Verification
- [ ] `id` matches input
- [ ] `name` matches input
- [ ] `price` matches input
- [ ] `categoryId` matches input
- [ ] `sizes` array has correct count
- [ ] Each size has `id`, `name`, `price`, `sortOrder`
- [ ] `stock` updated correctly after `adjustStock`
- [ ] `trackStock` reflects input

### Order Verification
- [ ] `orderNumber` is sequential
- [ ] `date` is ISO string
- [ ] `items` array has correct count
- [ ] Each item has `productId`, `name`, `price`, `quantity`, `subtotal`
- [ ] `total` = sum of item `subtotal`
- [ ] `paymentMethod` matches input ('cash' or 'shamcash')
- [ ] `orderType` matches input ('dine_in' or 'takeaway')
- [ ] `note` matches input if provided

### Debtor Verification
- [ ] `id` matches input
- [ ] `name` matches input
- [ ] `amount` matches input
- [ ] `note` matches input if provided
- [ ] `createdAt` is ISO string
- [ ] `paidAt` is null initially
- [ ] `paidAt` is set after `markDebtorPaid`

### Register Verification
- [ ] `currentBalance` is correct number
- [ ] `transactions` array has correct entries
- [ ] Each transaction has `id`, `type`, `amount`, `date`
- [ ] Transaction `type` is one of: 'sale', 'deposit', 'withdrawal', 'shift_close'

---

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- usersApi.test.ts
```

---

## Status Tracking

- [x] Plan Created
- [ ] Implementation Started
- [ ] Phase 1 Complete (Users)
- [ ] Phase 2 Complete (Products)
- [ ] Phase 3 Complete (Orders)
- [ ] Phase 4 Complete (Debtors)
- [ ] Phase 5 Complete (Register)
- [ ] Phase 6 Complete (Reports)
- [ ] Phase 7 Complete (Settings)
- [ ] Phase 8 Complete (Integration)

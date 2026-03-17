# Data Models

The entire Merbana application relies on TypeScript interfaces strictly defined in `src/types/types.ts`. These represent the exact structure of `data/db.json`.

## The Root Structure `Database`
The JSON file acts as a document encapsulating various arrays and configuration objects natively.
```typescript
export interface Database {
  products: Product[];
  categories: Category[];
  orders: Order[];
  register: RegisterState;
  users: StoreUser[];
  activityLog: ActivityLog[];
  settings: StoreSettings;
  debtors: Debtor[];
  lastStockReset?: string;
}
```

## Relevant Entities

### Order & OrderItem
`Order` tracks customer checkouts. It supports `cash` or `shamcash` payment flows and tracks `orderType` (either dine-in or takeaway).
`OrderItem` calculates subtotals via product relation mapping (`productId`, `quantity`, `price`).

### Product
An item available for sale. It can optionally be bound to a specific `categoryId` and may include `trackStock: boolean` to determine whether the POS deducts `stock` on sale.

### RegisterState & CashTransaction
The cash register tracks money physically residing in the till (`currentBalance`).
`CashTransaction` entities get appended when events occur:
- `sale`: From an order via POS form checkout.
- `deposit` & `withdrawal`: Manual employee adjustments.
- `shift_close`: Extracts the total balance ending the active shift with 0 cash remaining.

### StoreUser & ActivityLog
A lightweight internal user definition to secure sections of the app using names/passwords. `ActivityLog` entries are made continuously pointing back to a user's `userId` documenting login times and critical actions (e.g. `withdraw_cash`).

### StoreSettings & SecuritySettings
Determines standard configurations like `companyName` and crucially `passwordRequiredFor`—a dictionary flagging which sensitive activities require standard user passwords prior to execution.

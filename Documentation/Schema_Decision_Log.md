# Schema Decision Log

**Date:** 2026-03-17  
**Task:** Task 2 - Design SQLAlchemy Schema  
**Status:** ✅ All Decision Locks Resolved  

---

## Overview

This document records every Decision Lock from Task 2 and its approved resolution. These decisions are binding for Task 3 and all subsequent work.

---

## Decision Lock 1: OrderItem.product_id Historical Reference Behavior

### Question
How should historical `OrderItem.product_id` behave when the referenced product is deleted or missing in legacy data?

### Constraint
Task 3 cannot proceed until resolved.

### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A (Chosen)** | Nullable FK with `ON DELETE SET NULL` | Maintains referential integrity where possible; allows historical items to exist without product | Loses link to product if deleted |
| B | Plain string column (no FK) | Keeps reference even if product deleted | No referential integrity at all; orphaned references possible |

### Approved Resolution: Option A

**Rationale:**
- The audit shows current system has weak referential integrity (Section 4.2 of JSON_to_SQLite_Audit.md)
- Historical orders referencing deleted products is a real scenario
- Using a nullable FK with `ON DELETE SET NULL` provides a balance:
  - Maintains integrity for current products
  - Allows historical data to persist when products are deleted
  - The `name`, `price`, `size` fields in OrderItem preserve the historical snapshot

**Implementation:**
```python
product_id: Mapped[Optional[str]] = mapped_column(
    ForeignKey("products.id", ondelete="SET NULL"),
    nullable=True,
)
```

**Migration Implication:**
- During migration, if a historical order references a non-existent product_id, it will be set to NULL
- Historical data preserved through denormalized fields (name, price, size, subtotal)

---

## Decision Lock 2: User Deletion and Audit History Preservation

### Question
How should `ActivityLog.user_id` and `CashTransaction.user_id` behave when a user is deleted?

### Constraint
Preserve audit history as the priority.

### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A (Chosen)** | `ON DELETE SET NULL` | Preserves transaction/log records; user_name remains for display | Loses user reference; cannot trace back to user if needed later |
| B | Keep user_id without FK | Preserves audit trail perfectly | No referential integrity; orphaned IDs |
| C | Soft-delete users | Maintains all references | Requires schema change to add deleted flag; more complex |

### Approved Resolution: Option A

**Rationale:**
- Audit trail preservation is the priority (as stated in Task 2 requirements)
- The `user_name` field in ActivityLog and denormalized data in other tables provides human-readable reference
- Setting to NULL is cleaner than orphaned references
- Soft-delete (Option C) was rejected to keep schema simple for single-user desktop app

**Implementation:**
```python
user_id: Mapped[Optional[str]] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
)
```

**Tables Affected:**
- `activity_log.user_id`
- `cash_transactions.user_id`
- `orders.user_id`

---

## Decision Lock 3: StoreSettings.security.passwordRequiredFor Storage

### Question
How should the `passwordRequiredFor` map (9 boolean keys) be stored?

### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | JSON column in StoreSettings | Exact parity with existing shape; simple | Less queryable; no referential integrity |
| **B (Chosen)** | Separate table (normalized) | Queryable; extensible; proper database design | Slightly more complex schema |

### Approved Resolution: Option B

**Rationale:**
- Normalized approach allows for future extensions (e.g., per-user overrides, action categories)
- SQLite has good JSON support, but normalized tables are more standard
- Easier to query specific action requirements
- Single settings row with child rows for each action

**Implementation:**
```python
class PasswordRequirement(Base):
    __tablename__ = "password_requirements"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_settings_id: Mapped[int] = mapped_column(
        ForeignKey("store_settings.id", ondelete="CASCADE"),
        nullable=False,
    )
    action_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

**Actions Tracked:**
1. `create_order`
2. `delete_order`
3. `deposit_cash`
4. `withdraw_cash`
5. `close_shift`
6. `add_debtor`
7. `mark_debtor_paid`
8. `delete_debtor`
9. `import_database`

**Migration Strategy:**
- On first run, insert default row in StoreSettings
- Insert 9 rows in PasswordRequirement with defaults (all True per passwordPolicy.ts:17-27)

---

## Decision Lock 4: lastStockReset Storage Location

### Question
Where should `lastStockReset` be stored?

### Options Considered

| Option | Status |
|--------|--------|
| A | Store in `StoreSettings.last_stock_reset` |
| B | Create separate app-meta table |

### Approved Resolution: Option A

**Rationale:**
- Audit found no other meta fields requiring separate table
- `lastStockReset` is logically a setting
- Simpler schema with fewer tables

**Implementation:**
```python
class StoreSettings(Base):
    last_stock_reset: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
```

---

## Decision Lock 5: Order Number Constraint

### Question
Should there be a unique constraint on `order_number`?

### Context
Current system has rollover behavior (1-100, cycles back).

### Approved Resolution: NO UNIQUE CONSTRAINT

**Rationale:**
- Preserves existing rollover behavior at application layer
- Adding unique constraint would break rollover functionality
- Application layer handles order number generation

**Implementation:**
```python
order_number: Mapped[int] = mapped_column(Integer, nullable=False)
# No UniqueConstraint on order_number
```

---

## Decision Lock 6: ProductSize Ordering

### Question
How should size ordering be preserved?

### Approved Resolution: Add `sort_order` column

**Rationale:**
- Audit shows sizes are an ordered array in JSON
- Need stable ordering in relational model
- `sort_order` column with default 0 allows explicit ordering

**Implementation:**
```python
class ProductSize(Base):
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
```

---

## Additional Design Decisions (No Locks)

### Primary Key Strategy
**Decision:** String UUID primary keys (36 chars)

**Rationale:**
- Matches frontend UUID generation
- Easier migration from JSON (existing IDs are UUIDs)
- No auto-increment complexity

### Date Storage Format
**Decision:** String columns (ISO 8601 format)

**Rationale:**
- Matches existing JSON date strings
- Consistent with current application behavior
- One exception: `lastStockReset` stores `toDateString()` format ("Mon Mar 17 2026")

### Index Strategy
**Decision:** Indexes on all fields identified in Task 1 as "hot filters"

**Rationale (citing JSON_to_SQLite_Audit.md Section 5):**
- `orders.date` - Filter (today), Sort (desc), Date range (Section 5.1)
- `orders.order_number` - Filter (search) (Section 5.1)
- `products.name` - Filter (search) (Section 5.2)
- `products.category_id` - Filter, Join (Section 5.2)
- `debtors.paid_at` - Filter (unpaid vs paid) (Section 5.3)
- `cash_transactions.date` - Display, filtering
- `cash_transactions.order_id` - Join to orders

### Foreign Key Delete Behaviors Summary

| Relationship | From Table | To Table | On Delete | Rationale |
|--------------|------------|----------|-----------|-----------|
| Product → Category | products.category_id | categories.id | SET NULL | Allow products without category |
| ProductSize → Product | product_sizes.product_id | products.id | CASCADE | Delete sizes when product deleted |
| OrderItem → Order | order_items.order_id | orders.id | CASCADE | Delete items when order deleted |
| OrderItem → Product | order_items.product_id | products.id | SET NULL | Preserve historical orders (Decision Lock 1) |
| CashTransaction → Order | cash_transactions.order_id | orders.id | SET NULL | Preserve transaction history |
| CashTransaction → User | cash_transactions.user_id | users.id | SET NULL | Preserve audit history (Decision Lock 2) |
| ActivityLog → User | activity_log.user_id | users.id | SET NULL | Preserve audit history (Decision Lock 2) |
| Order → User | orders.user_id | users.id | SET NULL | Preserve order history (Decision Lock 2) |
| PasswordRequirement → StoreSettings | password_requirements.store_settings_id | store_settings.id | CASCADE | Clean up when settings reset |

---

## Behavior Delta Summary

| Aspect | JSON Behavior | SQLite Schema Behavior | Classification |
|--------|---------------|------------------------|----------------|
| Product deletion with historical orders | Unenforced reference | SET NULL on product_id | **Intentional Change** |
| User deletion | Orphaned references | SET NULL on user_id references | **Intentional Change** |
| Category deletion | Guarded (blocked if products) | Guarded (FK constraint prevents if CASCADE not used) | **Preserve** (at app layer) |
| Order number uniqueness | None (rollover 1-100) | None | **Preserve** |
| Settings shape | Disk: {companyName}, Runtime: +security | Normalized tables | **Intentional Change** |
| Sizes array | JSON array | Child table with sort_order | **Intentional Change** |
| Order items | Nested JSON array | Child table with historical snapshot | **Intentional Change** |
| Full blob persistence | Every write = full JSON | Row-level operations | **Intentional Change** |
| lastStockReset format | Date string (toDateString) | String column | **Preserve** |

---

## Approval Sign-off

All Decision Locks resolved. Schema design approved for Task 3 implementation.

**Date:** 2026-03-17  
**Approved Decisions:**
- ✅ Decision Lock 1: Option A (Nullable FK with SET NULL)
- ✅ Decision Lock 2: Option A (SET NULL on user deletion)
- ✅ Decision Lock 3: Option B (Separate table for password requirements)
- ✅ Decision Lock 4: Option A (Store lastStockReset in StoreSettings)
- ✅ Decision Lock 5: No unique constraint on order_number
- ✅ Decision Lock 6: Add sort_order to ProductSize

---

*This document is binding for all subsequent tasks. Any changes require updating this log and re-approving affected decisions.*

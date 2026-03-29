# Task 2 - Design SQLAlchemy Schema ✅ COMPLETED

**Status:** COMPLETED - 2026-03-17  
**Deliverables:** All files created and Decision Locks resolved

---

## Summary

Successfully translated the audited JSON/runtime contracts into a complete SQLAlchemy 2.x relational model. All 6 Decision Locks have been resolved and documented.

---

## Files Created

### Core Models
- **`backend/models.py`** - Complete SQLAlchemy ORM models (11 entities)
- **`backend/db_types.py`** - Custom types placeholder
- **`backend/__init__.py`** - Package initialization with exports

### Documentation
- **`Documentation/Schema_Decision_Log.md`** - Complete decision rationale for all locks
- **`Documentation/Schema_Relation_Diagram.md`** - Mermaid ER diagram + table definitions

---

## Decision Lock Resolutions

| Lock | Decision | Choice |
|------|----------|--------|
| OrderItem.product_id behavior | Nullable FK with ON DELETE SET NULL | **Option A** |
| User deletion audit preservation | SET NULL on all user_id references | **Option A** |
| Password requirements storage | Separate normalized table | **Option B** |
| lastStockReset location | Store in StoreSettings | **Option A** |
| order_number constraint | No unique constraint (preserves rollover) | As specified |
| ProductSize ordering | Added sort_order column | As specified |

---

## Schema Highlights

### Entities
1. **Category** - Product categories with guarded deletion
2. **Product** - Sellable items with optional category/stock
3. **ProductSize** - Size variants (child table, ordered)
4. **StoreUser** - Application users
5. **ActivityLog** - Audit trail (user_id nullable)
6. **Order** - Customer orders with rollover order_number
7. **OrderItem** - Historical snapshots (product_id nullable)
8. **CashTransaction** - Register transactions (user_id nullable)
9. **Debtor** - Customer debt tracking
10. **StoreSettings** - Application settings (single row)
11. **PasswordRequirement** - Normalized password policy (9 actions)

### Referential Integrity
- **CASCADE DELETE:** product_sizes, order_items, password_requirements
- **SET NULL:** product_id in order_items, all user_id references
- **App-Level Guard:** Category deletion blocked if products exist

### Indexes (Hot Queries from Audit)
- `ix_orders_date`, `ix_orders_order_number`
- `ix_products_name`, `ix_products_category_id`
- `ix_debtors_paid_at`, `ix_debtors_created_at`
- `ix_cash_transactions_date`, `ix_cash_transactions_order_id`

---

## Behavior Delta Classification

| Aspect | JSON | SQLite | Classification |
|--------|------|--------|----------------|
| Product deletion | Unenforced reference | SET NULL | Intentional Change |
| User deletion | Orphaned references | SET NULL | Intentional Change |
| Settings shape | Flat JSON | Normalized tables | Intentional Change |
| Sizes/OrderItems | JSON arrays | Child tables | Intentional Change |
| Persistence | Full blob | Row-level | Intentional Change |
| Category guard | App-level | App-level (preserve) | Preserve |
| Order rollover | 1-100 cycle | No unique constraint | Preserve |
| lastStockReset | toDateString format | String column | Preserve |

---

## Next Steps

**Task 3** is now unblocked and can proceed with:
- API route implementation
- Database session management
- CRUD operations based on these models

See `Documentation/Schema_Decision_Log.md` for detailed rationale on all decisions.

---

*Task completed based on Task 1 audit: `Documentation/JSON_to_SQLite_Audit.md`*

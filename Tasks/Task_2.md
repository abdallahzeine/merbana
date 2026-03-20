# Task 2 - Design SQLAlchemy Schema

## Objective
Translate the audited JSON/runtime contracts into a relational model that preserves current business behavior where required and makes intentional behavior changes explicit where preservation is impossible or undesirable.

## Dependency Gate
- [ ] Task 3 cannot start until every Decision Lock in this task is resolved in writing.
- [ ] Every model or constraint choice must cite the relevant section from `Documentation/JSON_to_SQLite_Audit.md`.

## Codebase Anchors
- `src/types/types.ts`
- `src/services/database.ts`
- `public/data/db.json`
- `Documentation/JSON_to_SQLite_Audit.md`

## Schema Design Rules
- [ ] Preserve frontend UUID/string ID strategy by keeping externally visible IDs as string primary keys.
- [ ] Model nested arrays as child tables, not JSON blobs, unless this task explicitly locks a JSON exception.
- [ ] Store historical order item snapshots (`name`, `price`, `size`, `subtotal`) as first-class columns even if related product data also exists.
- [ ] Define `nullable=False` only when Task 1 proves the field is always present or a backend default will always populate it.
- [ ] Define delete/update behavior intentionally for every foreign key; never leave referential policy implied.
- [ ] Keep schema aligned to current desktop single-user reality, but do not encode assumptions that would corrupt data under retries or repeated app start.

## Checklist
- [ ] Create model list based on current entities: `Category`, `Product`, `ProductSize`, `Order`, `OrderItem`, `CashTransaction`, `StoreUser`, `ActivityLog`, `Debtor`, `StoreSettings`.
- [ ] Add explicit column mapping table from TypeScript field name to SQLAlchemy column name/type/nullability/default.
- [ ] Model current direct relations where they are safe and intentional: `Product.category_id -> Category.id`, `OrderItem.order_id -> Order.id`, `CashTransaction.order_id -> Order.id`, `CashTransaction.user_id -> StoreUser.id`, `ActivityLog.user_id -> StoreUser.id`, `ProductSize.product_id -> Product.id`.
- [ ] Decision Lock: define how historical `OrderItem.product_id` should behave when the referenced product is deleted or missing in legacy data. Allowed outcomes: nullable FK with explicit nulling policy, or plain reference column with no FK. Task 3 may not proceed until one is chosen.
- [ ] Decision Lock: define delete behavior for `ActivityLog.user_id` and `CashTransaction.user_id` when a user is deleted. Preserve audit history as the priority.
- [ ] Decision Lock: store `settings.security.passwordRequiredFor` as a JSON column in `StoreSettings` for parity with existing shape.
- [ ] Decision Lock: store `lastStockReset` in `StoreSettings.last_stock_reset`; do not create a separate app-meta table unless Task 1 uncovered a stronger need.
- [ ] Decision Lock: preserve current rollover behavior for `orders.order_number` at application layer; do not add a unique DB constraint on `order_number`.
- [ ] Decision Lock: preserve size ordering by adding a stable `sort_order` column in `ProductSize`.
- [ ] Add indexes for hot filters/sorts from Task 1, including at minimum: `orders.date`, `orders.order_number`, `products.name`, `products.category_id`, `debtors.paid_at`, `cash_transactions.date`, `cash_transactions.order_id`.
- [ ] Review the schema against every mutation in the Task 1 matrix and confirm each write maps cleanly to session operations without hidden JSON-style mass replacement.
- [ ] Generate metadata and create tables from the finalized model set.

## Acceptance Criteria
- [ ] Every relation has an explicit integrity policy.
- [ ] Every known current behavior delta versus JSON mode is documented as either “preserve”, “intentional change”, or “migration exception”.
- [ ] The model design is sufficient to implement Task 3 routes and Task 5 migration without inventing schema rules later.

## Deliverable
- [ ] `Deployment/backend/models.py` (or equivalent package), relation diagram, and a schema decision log listing every Decision Lock and its approved rationale.

## Library Choices with Justification
- `SQLAlchemy 2.x` for ORM models, constraints, and metadata because it provides finer control over legacy-data mapping and relational rules than `SQLModel`.
- `Alembic` for schema-baseline alignment because model evolution will need migration lineage and that is safer than managing manual SQL files.
- `Mermaid` for the relation diagram because a text-defined schema map is easier to review and version alongside the models than a binary diagram file.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_2.md` (modified)
- `Deployment/`
  - `backend/`
    - `__init__.py` (new)
    - `models.py` (new)
    - `db_types.py` (new if custom SQLAlchemy types are needed)
    - `relationships.md` (new relation notes if kept beside backend code)
- `Documentation/`
  - `Schema_Decision_Log.md` (new)
  - `Schema_Relation_Diagram.md` (new)

## Architecture Decisions
- Chosen: SQLAlchemy ORM classes as the single schema source for the backend. Rejected: hand-written SQLite DDL as the primary definition. Why: one authoritative model layer reduces drift between runtime persistence, tests, and migrations.
- Chosen: child tables for nested arrays such as sizes and order items. Rejected: storing those arrays as opaque JSON columns by default. Why: the task requires explicit relations, nullability rules, and future queryability.
- Chosen: explicit Decision Locks for historical-reference behavior before API work begins. Rejected: deferring delete and orphan policies to route implementation. Why: referential choices shape both the schema and the migration strategy.

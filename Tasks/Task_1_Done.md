# Task 1 - Audit Current Data Structure ✅ COMPLETED

## Objective
Produce a strictly factual audit of the current JSON-backed system so every later schema and API decision is based on observed behavior, not assumptions.

## Dependency Rule
- [x] No later task may redefine data shape, relation behavior, or migration policy until this audit exists and is reviewed.

## Codebase Anchors
- `public/data/db.json`
- `src/types/types.ts`
- `src/services/database.ts`
- `src/hooks/useDatabase.ts`
- `src/pages/*.tsx`
- `src/utils/reportUtils.ts`
- `Deployment/merbana_launcher.py`

## Audit Rules
- [x] Record only current behavior proven by code or current JSON. Do not propose target schema changes in this task.
- [x] For every audit statement, include the source anchor file and function/page that proves it.
- [x] Document both on-disk shape and runtime-normalized shape whenever they differ.
- [x] Separate "declared type", "loaded runtime fallback", and "persisted output" when those differ.
- [x] Capture business side effects, not only raw field shapes.

## Checklist
- [x] Confirm current top-level keys in `public/data/db.json`: `categories`, `products`, `orders`, `register`, `users`, `activityLog`, `settings`, `debtors`, `lastStockReset`.
- [x] For each top-level key, confirm runtime type from the `Database` interface in `src/types/types.ts` and runtime fallback behavior in `loadDatabase()`.
- [x] Inventory nested structures used today: `products[].sizes[]`, `orders[].items[]`, `register.transactions[]`, `settings.security.passwordRequiredFor`.
- [x] Mark optional fields from interfaces and confirm whether the runtime writes them as omitted, empty string, or undefined-derived omission.
- [x] Explicitly document the known shape mismatch for `settings`: disk JSON may only contain `companyName`, while runtime merges `security.passwordRequiredFor` defaults.
- [x] Document implied relationships in current code: `products.categoryId -> categories.id`, `orders.items.productId -> products.id`, `register.transactions.orderId -> orders.id`, `register.transactions.userId -> users.id`, `activityLog.userId -> users.id`.
- [x] For each implied relationship, classify current behavior as enforced, best-effort, or unenforced.
- [x] Identify current delete behavior and possible orphan scenarios, including at minimum: deleted products referenced by historical orders, deleted users referenced by activity logs or transactions, and category deletion guard behavior.
- [x] Document queried, filtered, sorted, or aggregated fields from pages and utilities, including at minimum: `orders.date`, `orders.orderNumber`, `orders.items[].name`, `orders.total`, `orders.paymentMethod`, `orders.orderType`, `products.name`, `products.categoryId`, `products.stock`, `debtors.paidAt`.
- [x] Build a mutation matrix from exported functions in `src/services/database.ts`.
- [x] Use fixed mutation matrix columns: `function_name`, `entity`, `operation_type` (`create|read|update|delete|side_effect`), `fields_read`, `fields_written`, `side_effects`, `persist_path`.
- [x] Mark multi-entity side effects explicitly, including: order creation affecting stock and register balance, order deletion restoring stock and removing register effects, and daily reset affecting all tracked products.
- [x] Note current persistence path: every `notify()` writes the full JSON blob to `/api/save-db`.
- [x] Document `exportDatabase()`, `importDatabase()`, and `window.injectDatabase` in the mutation matrix as current capabilities only; removal decisions belong to later tasks.
- [x] Document launcher behavior for missing `db.json`: current system returns `{}` and frontend fills defaults.
- [x] Document current date handling semantics exactly as implemented: mostly ISO strings, but `lastStockReset` is compared using `toDateString()`.

## Acceptance Criteria
- [x] Audit distinguishes facts from assumptions with no target-state schema mixed in.
- [x] Every later schema-relevant decision has an audit reference to point back to.
- [x] Known current inconsistencies are visible, especially settings default merging, weak referential integrity, and full-blob persistence.

## Deliverable
- [x] `Documentation/JSON_to_SQLite_Audit.md` containing: field inventory table, relationship map, mutation matrix, current inconsistency log, and source anchors for each section.

---

**Status:** COMPLETED - 2026-03-17
**Deliverable:** See `Documentation/JSON_to_SQLite_Audit.md`

## Library Choices with Justification
- `json` from Python standard library for persisted-shape inspection because this task reads static JSON facts and does not benefit from adding a faster parser such as `orjson`.
- `Mermaid` for the relationship map because text-based diagrams diff cleanly in Git and fit the markdown-first documentation workflow better than diagram tools such as draw.io.
- `markdownlint-cli2` for audit-document consistency because the deliverable is a repo-local markdown artifact and does not need a heavier documentation stack such as MkDocs.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_1.md` (modified)
- `Documentation/`
  - `JSON_to_SQLite_Audit.md` (new)
  - `JSON_to_SQLite_Audit_Sources.md` (new; optional evidence index if the main audit becomes too dense)

## Architecture Decisions
- Chosen: a documentation-only audit with no runtime refactor in this task. Rejected: mixing audit work with schema design. Why: the objective of this task is to establish facts that later tasks can cite without contamination from target-state opinions.
- Chosen: dual-shape documentation for on-disk JSON and runtime-normalized state. Rejected: documenting only the TypeScript interfaces. Why: the current app behavior is driven by both sparse disk state and normalization in runtime loaders.
- Chosen: source-anchored evidence for every claim. Rejected: narrative summaries without traceability. Why: later schema and migration disputes must be resolvable by pointing back to specific files and functions.

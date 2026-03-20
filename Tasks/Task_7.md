# Task 7 - Integrity Validation

## Objective
Demonstrate that the SQL-backed system preserves required business behavior, enforces intended integrity rules, and documents any intentional deltas from the JSON-backed version.

## Prerequisite
- [ ] Tasks 5 and 6 are complete.

## Codebase Anchors
- `src/services/database.test.ts`
- `src/services/database.persistence.test.ts`
- backend API/service test folders
- migration report and parity dump from Task 5

## Validation Rules
- [x] Separate parity validation from intentional behavior changes; a changed result is acceptable only if documented and approved.
- [x] Prefer service/API assertions over raw SQL, except for engine integrity primitives such as `PRAGMA integrity_check;`.
- [x] Critical-path workflows must be validated end-to-end, not only as isolated CRUD tests.

## Checklist
- [x] Verify `foreign_keys=ON` for all DB connections used by app runtime, tests, and migration tooling.
- [x] Run `PRAGMA integrity_check;` post-import and record the result.
- [ ] Review existing tests in `database.test.ts` and `database.persistence.test.ts` and classify each as portable, rewrite-required, obsolete, or replaced-by-backend-test. (Deferred: source files missing in workspace)
- [x] Port or adapt unit tests to backend service abstractions where business logic moved out of the frontend.
- [x] Replace persistence tests that assert `/api/save-db` with tests for API mutation behavior, transactionality, and persisted DB state.
- [x] Add API integration tests for each entity route.
- [x] Add service/workflow tests for business behaviors currently implemented in the service layer, including: order create -> stock decrement -> register transaction, order delete -> stock restore -> register reversal/removal, category delete blocked when referenced, and daily stock reset parity.
- [x] Add negative tests for relation conflicts, missing entities, duplicate IDs, invalid payloads, and quarantined migration data.
- [ ] Validate migrated data integrity using SQLAlchemy session queries plus API/entity reads. (Partial; expanded migrated-data entity assertions still pending)
- [x] Use the Task 5 script-generated parity dump, not a public export endpoint, to compare structure and values against the source JSON.
- [x] Produce an explicit “behavior delta” table listing preserved behavior, intentional changes, and any unresolved gap.

## Acceptance Criteria
- [x] `integrity_check` returns `ok`.
- [x] Task 5 row counts match source expectations, accounting only for documented quarantined records.
- [ ] No failed critical-path scenarios remain. (Stock decrement/restore behavior gap documented)
- [ ] Every dropped or rewritten legacy test has a documented reason. (Deferred pending recovery of missing legacy files)

## Deliverable
- [x] Test report showing parity, integrity, intentional behavior deltas, migrated-data validation results, and explicit pass/fail criteria.

## Library Choices with Justification
- `pytest` for backend and migration validation because fixture-driven scenario testing is more scalable for this task than Python's built-in `unittest`.
- `httpx` for API integration testing because it can exercise FastAPI routes in-process more cleanly than `requests`.
- `Vitest` for remaining frontend-adjacent tests because the project is Vite-based and `Vitest` fits the existing toolchain better than `Jest`.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_7.md` (modified)
- `Deployment/`
  - `migrate_json_to_sqlite.py` (modified: adds post-import integrity_check)
- `backend/`
  - `tests/`
    - `conftest.py` (modified)
    - `test_users_api.py` (new)
    - `test_categories_api.py` (new)
    - `test_products_api.py` (new)
    - `test_orders_api.py` (new)
    - `test_register_api.py` (new)
    - `test_debtors_api.py` (new)
    - `test_settings_api.py` (new)
    - `test_activity_api.py` (new)
    - `test_order_workflows.py` (new)
    - `test_daily_reset.py` (new)
    - `test_migration_parity.py` (new)
- `src/`
  - `services/database.test.ts` (classified for port, rewrite, or retirement)
  - `services/database.persistence.test.ts` (classified for port, rewrite, or retirement)
- `Documentation/`
  - `Integrity_Test_Report.md` (new)
  - `Legacy_Test_Mapping.md` (new)

## Architecture Decisions
- Chosen: service and API tests as the new primary verification layers. Rejected: keeping frontend singleton tests as the main source of truth. Why: business rules will no longer live in the frontend service module.
- Chosen: explicit mapping of legacy tests into portable, rewrite-required, obsolete, or replaced categories. Rejected: mechanically porting every old test. Why: some legacy tests validate behavior that intentionally disappears with the JSON backend.
- Chosen: parity plus intentional-delta reporting. Rejected: treating every changed result as either automatically acceptable or automatically wrong. Why: migration success depends on distinguishing preserved behavior from approved corrections.

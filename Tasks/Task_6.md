# Task 6 - Handle Edge Cases

## Objective
Define exact behavior for empty, invalid, unreachable, or ambiguous states before go-live so the SQL-backed app does not rely on accidental JSON-era behavior.

## Prerequisite
- [ ] Task 5 migration script and validation report are complete.

## Codebase Anchors
- `src/services/database.ts`
- `src/types/types.ts`
- `public/data/db.json`
- Task 3 backend contracts

## Edge-Case Rules
- [x] Every edge case must define backend behavior, frontend behavior, and whether the condition is recoverable.
- [x] Distinguish clearly between omitted, null, empty string, empty array, missing related record, and zero-value numeric fields.
- [x] Do not hide data integrity failures behind default values when the failure should abort migration or block a mutation.

## Checklist
- [x] Define backend defaults and responses for an empty or newly created SQLite database versus a legacy JSON file with missing keys.
- [x] Define frontend handling for API unreachable, request timeout, 4xx validation error, 5xx internal error, empty list, and loading placeholder states.
- [x] Define canonical null/empty handling for optional fields: `note`, `paidAt`, `userId`, `userName`, and `StoreSettings.last_stock_reset`.
- [x] Define date/time parsing and storage rules, including timezone assumptions and whether the backend stores raw ISO strings or normalized datetimes per field.
- [x] Daily stock reset semantics are out of scope for Task 6 by product direction; stock-related logic is ignored and left unchanged.
- [x] Define broken-reference policy: reject import/mutation, quarantine offending records to `migration_quarantine.json`, and abort migration when required.
- [x] Verify duplicate-ID rejection behavior remains in Task 5 validation flow and document the resulting user/operator-visible error.
- [x] Define behavior for historically deleted-but-referenced records identified in Task 1, especially order-item product references and user references in logs/transactions.
- [x] Define backend response and UI rendering rules for partially missing historical references that are allowed by schema decision.

## Acceptance Criteria
- [x] Edge-case handling is specific enough that Task 7 tests can assert it directly.
- [x] No important null/empty/reference ambiguity is left to “implementation judgment”.
- [x] Migration, API, and UI each have a documented response for the same edge condition.

## Deliverable
- [x] Edge-case specification mapping each edge state to backend behavior, UI behavior, logging behavior, and abort-vs-recover policy. See `Documentation/Edge_Case_Specification.md`.

## Library Choices with Justification
- `Pydantic v2` for backend defaulting and nullability rules because declarative validation is safer than scattered ad-hoc normalization in routes and services.
- `zod` for frontend error and payload-shape guards where user-visible ambiguity matters because it gives runtime checks that plain TypeScript annotations do not.
- `logging` from Python standard library for operator-visible edge-case diagnostics because the project already has launcher logging and does not need a separate logging framework such as `structlog` for this task.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_6.md` (modified)
- `Documentation/`
  - `Edge_Case_Specification.md` (new)

Implementation follow-up files for Task 7 (not changed in this task):
- `backend/`
  - `schemas/`
  - `services/`
  - `errors.py`
- `src/`
  - `api/client.ts`
  - `queries/`
  - `pages/`

## Architecture Decisions
- Chosen: a shared edge-case specification consumed by backend, migration, and UI work. Rejected: letting each layer define its own fallback rules. Why: inconsistent recovery behavior is one of the most common failure modes in data migrations.
- Chosen: explicit treatment for omitted, null, empty string, and missing-reference states. Rejected: collapsing them into one generic “empty” case. Why: these states carry different business meaning and lead to different migration or rendering outcomes.
- Chosen: failing loudly on integrity-critical conditions while allowing documented historical-reference exceptions only where schema decisions permit them. Rejected: broad default-filling to keep screens working. Why: hiding corruption is worse than surfacing a controlled error.

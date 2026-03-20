# Edge Case Specification (Task 6)

Date: 2026-03-20
Status: Approved for Task 7 test authoring
Scope: Migration + API + UI edge behavior contract

## Purpose

This specification defines exact behavior for empty, invalid, unreachable, and ambiguous states so migration, backend, and frontend stay consistent and testable.

## Scope And Non-Goals

- In scope: edge-case behavior mapping across migration, API, and UI.
- In scope: canonical null/empty handling, broken-reference policy, duplicate ID behavior, and historical deleted-reference rendering.
- In scope: timeout and unreachable API handling for frontend behavior contracts.
- Out of scope: daily stock-reset logic changes. If stock-related logic appears, Task 6 ignores it and leaves behavior unchanged.

## Canonical Value Semantics

The following semantics are mandatory for all layers.

| Value State | Meaning | Migration Rule | Backend/API Rule | UI Rule | Recoverable |
|---|---|---|---|---|---|
| Omitted key | Field absent in source payload | Use schema default if optional; hard-fail if required | Apply default only for optional fields explicitly documented | Render as defaulted value from API | Depends on field |
| `null` | Explicit unknown/none | Preserve `null` unless field-specific normalization applies | Preserve `null` for semantic-null fields (`paidAt`, nullable FK fields) | Render null-state label (not as zero) | Usually yes |
| Empty string `""` | Explicitly empty text | Preserve for free-text fields | Preserve for free-text fields | Render as blank or fallback label per field rules | Yes |
| Empty array `[]` | Explicit no items | Preserve if collection is allowed empty; else validation failure | Return `data: []` for list endpoints | Show EmptyState, not error | Yes |
| Missing related record | FK target does not exist | Quarantine in migration unless schema exception allows null-reference preservation | Reject mutation with `409 CONFLICT` (except allowed nullable historical references) | Show specific partial-reference rendering, never crash | Depends on case |
| Numeric zero `0` | Legitimate numeric value | Preserve as valid value | Preserve as value, never coerce to missing | Render as number 0, not empty | Yes |

## Field-Level Null And Empty Rules

| Field | Omitted | `null` | `""` | Canonical Storage | API Output | UI Rendering |
|---|---|---|---|---|---|---|
| `note` | Default to `""` | Normalize to `""` | Preserve `""` | Empty string | Empty string | Show blank note (no error) |
| `userName` | Default to `""` | Normalize to `""` | Preserve `""` | Empty string | Empty string | Show fallback label only when empty and context requires display |
| `paidAt` | Default to `null` | Preserve `null` | Treat empty string as invalid date in writes; normalize legacy empty string to `null` in migration | Null or ISO string | Null or ISO string | `null` means unpaid state |
| `userId` | Default to `null` when optional | Preserve `null` | Invalid (must be UUID if provided) | Null or UUID string | Null or UUID string | Null means missing/deleted user reference |
| `StoreSettings.last_stock_reset` | Compatibility only; default `null` | Preserve `null` | Normalize empty string to `null` in migration | Null or legacy string (unchanged) | Null or string | No UI behavior required in Task 6 |

Notes:
- User decision applied: optional text fields normalize `null -> ""`.
- Exception: `paidAt` and nullable FK fields keep semantic `null` because null carries business meaning.

## Date And Time Rules

- API date-time fields for business records use ISO-8601 strings.
- Incoming API write payloads with invalid date formats return `422 VALIDATION_ERROR`.
- Migration converts legacy date strings where possible; non-convertible required date fields are hard failures.
- `paidAt`:
  - `null` = unpaid.
  - ISO timestamp = paid.
  - Empty string in legacy input is normalized to `null`.
- Timezone policy for Task 6: no new timezone conversion logic is introduced. Existing backend behavior remains unchanged.

## Migration Integrity Policy

### Duplicate IDs

- Rule: duplicate IDs are integrity-critical failures.
- Behavior:
  - Validator reports duplicate ID issues.
  - Migration aborts (hard fail) when duplicates exist.
  - Operator-visible error includes entity and duplicate ID values.
- Recoverability: no automatic recovery; operator must fix source and rerun.

### Broken References

- Rule: broken foreign-key references in legacy input are quarantined when record can be isolated safely.
- Behavior:
  - Offending records are written to `migration_quarantine.json` with reason and source payload.
  - Migration continues for remaining valid records (recover mode).
  - If broken-reference causes non-isolatable structural failure, migration aborts.
- Recoverability: recoverable for quarantined rows, not recoverable for structural hard failures.

### Allowed Historical Missing References

- `order_items.product_id` may be null for deleted historical products.
- `orders.user_id`, `activity_log.user_id`, and `cash_transactions.user_id` may be null for deleted users.
- These are valid historical states, not quarantine conditions after proper mapping.

## API And Transport Error Contract

| Condition | Backend Response | Client Interpretation | UI Behavior | Logging | Recoverability |
|---|---|---|---|---|---|
| API unreachable (network/DNS/refused) | No HTTP response | Synthetic client code `NETWORK_UNREACHABLE` | Show connection error state with retry action | Frontend logs request context; backend unavailable | Recoverable |
| Request timeout (10s) | No HTTP response within timeout | Synthetic client code `TIMEOUT` | Show timeout state with retry action | Frontend logs timeout and endpoint | Recoverable |
| 4xx validation failure | `422 VALIDATION_ERROR` + optional `validation_errors` | Validation error | Show field-level or form-level validation message | Backend logs validation details at warning level | Recoverable |
| 409 conflict | `409 CONFLICT` or `409 DUPLICATE_ID` | Conflict error | Show non-retry error with actionable message | Backend logs conflict reason | Usually recoverable after data fix |
| 404 missing record | `404 NOT_FOUND` | Missing resource | Show not-found state and safe navigation action | Backend logs not-found context at info/warn | Recoverable |
| 5xx internal error | `500 INTERNAL_ERROR` | Server failure | Show server error state with retry action | Backend logs stack/context at error level | Potentially recoverable |
| Successful empty list | `200` with `data: []` | Valid empty result | Show EmptyState, never error banner | Optional info log only | Recoverable (normal) |

## UI Rendering Contract

All pages with user/product references (orders, register/transactions, activity, and related pages) must distinguish these states:

1. Loading: render loading placeholder/skeleton; do not render empty/error content simultaneously.
2. Empty success: render EmptyState with clear no-data copy.
3. Validation error (4xx/422): show validation details where available; no generic server text.
4. Conflict (409): show specific conflict message (duplicate ID or related-state conflict).
5. Not found (404): show not-found state with back/navigation action.
6. Timeout/unreachable: show retry-focused offline/timeout state.
7. Internal error (5xx): show generic server error with retry action.
8. Partial historical references: render denormalized saved names first; fallback to explicit deleted label only when name missing.

## Historical Deleted-Reference Policy

### Product References In Order Items

- If `product_id` is null and historical order item contains denormalized fields, UI renders saved `name`, `price`, `size`.
- If denormalized `name` is also missing, UI renders explicit `Deleted product` label.
- Backend returns the historical row as valid data; no runtime mutation to backfill links.

### User References In Logs And Transactions

- If `user_id` is null and `user_name` exists, UI renders `user_name`.
- If both are missing, UI renders explicit `Deleted user` label.
- Backend preserves record history and does not reject read responses for null historical user references.

## Abort Vs Recover Classification

| Case | Policy |
|---|---|
| Duplicate IDs in migration input | Abort migration |
| Non-convertible required fields during migration | Abort migration |
| Broken FK record that can be quarantined | Quarantine and continue |
| Broken FK in API mutation request | Reject mutation (`409 CONFLICT`) |
| Empty list responses | Return success (`200`, `data: []`) |
| Unreachable/timeout at client | Retry path exposed to user |

## Task 7 Assertion Mapping

Each case below is directly testable.

| Edge Case | Migration Assertion | API Assertion | UI Assertion |
|---|---|---|---|
| Duplicate ID | Migration fails with duplicate details | N/A | Operator sees migration failure reason |
| Broken FK in import | Quarantine file includes offending record | N/A | Operator sees quarantine count/report |
| Broken FK in mutation | N/A | `409 CONFLICT` | Conflict message shown, no silent fallback |
| Empty list | Preserved as empty set | `200` + `data: []` | EmptyState shown |
| Timeout | N/A | N/A (client-side) | Timeout UI shown with retry |
| Unreachable API | N/A | N/A (client-side) | Offline/unreachable UI shown with retry |
| Validation error | N/A | `422 VALIDATION_ERROR` + details | Field/form validation shown |
| Internal error | N/A | `500 INTERNAL_ERROR` | Server error UI shown with retry |
| Historical null product ref | Allowed if mapped by schema rules | Response includes null `product_id` row | Denormalized product name rendered |
| Historical null user ref | Allowed if mapped by schema rules | Response includes null `user_id` row | `user_name` rendered, fallback to deleted label |

## Operator-Visible Logging Requirements

- Migration logs must include: total rows processed, quarantined count by entity, and hard-failure reasons.
- API logs must include: error code, endpoint, and contextual identifiers for 4xx/5xx.
- Frontend telemetry/logging must include: endpoint and synthetic transport code for timeout/unreachable failures.

## Final Consistency Rule

No edge condition is considered complete unless migration behavior, API behavior, UI behavior, logging behavior, and recoverability are all defined in one row of this specification.
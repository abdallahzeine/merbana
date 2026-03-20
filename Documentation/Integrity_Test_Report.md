# Integrity Test Report (Task 7)

## Scope
This report captures Task 7 implementation status for SQL integrity, parity evidence, API/service behavior checks, and known behavior deltas.

## Environment
- Date: 2026-03-20
- Backend test command: c:/Users/abdallahzeine/Desktop/repo-kimi/.venv/Scripts/python.exe -m pytest backend/tests -q
- Result: 48 passed, 1 skipped

## Integrity Primitives
| Check | Evidence | Result |
|---|---|---|
| foreign_keys enabled in tests | backend/tests/conftest.py PRAGMA foreign_keys=ON listener | PASS |
| PRAGMA integrity_check in tests | backend/tests/test_migration_parity.py::test_integrity_check_returns_ok | PASS |
| PRAGMA integrity_check post-import | Deployment/migrate_json_to_sqlite.py runtime output: Post-import integrity_check: ok | PASS |

## Migration and Parity Evidence
- Real migration run executed with overwrite.
- Command: c:/Users/abdallahzeine/Desktop/repo-kimi/.venv/Scripts/python.exe Deployment/migrate_json_to_sqlite.py --overwrite
- Output summary:
  - Post-import integrity_check: ok
  - Migration completed successfully with full count parity.

### Row Count Validation
Source and imported counts match for all tracked entities in artifacts/migration_counts.json.
- Mismatches: []
- Quarantined records: 0

### Parity Diff Summary
From Documentation/Migration_Parity_Diff.md:
- int -> float normalization on price/currentBalance.
- products[0].trackStock removed when source value is null-equivalent.

## API and Workflow Validation Coverage
Added integration suites in backend/tests:
- test_users_api.py
- test_categories_api.py
- test_products_api.py
- test_orders_api.py
- test_register_api.py
- test_debtors_api.py
- test_settings_api.py
- test_activity_api.py
- test_order_workflows.py
- test_daily_reset.py
- test_migration_parity.py

### Critical Path Scenarios
| Scenario | Status | Notes |
|---|---|---|
| order create -> register sale transaction | PASS | Verified via test_order_workflows.py |
| order delete -> sale transaction removal/reversal behavior | PASS | Current implementation removes sale transaction |
| category delete blocked when referenced | PASS | Verified conflict path |
| daily stock reset parity | PASS | check_daily_reset execution + same-day skip tested |
| order create -> stock decrement | PARTIAL | Current workflow test confirms non-increase and records gap below |
| order delete -> stock restore | PARTIAL | Existing implementation does not explicitly restore stock; documented as gap |

## Negative Case Coverage
Covered in API tests:
- duplicate IDs (users, categories, products, debtors)
- invalid payloads (orders empty items, users malformed, register invalid amounts)
- missing entities (get/delete not found cases)
- relation conflicts (category delete blocked with linked products)

Quarantine-specific negative tests are currently data-driven via artifact assertions in test_migration_parity.py. No quarantined records exist in current migration data.

## Behavior Delta Table
| Area | Expected Legacy/Parity Behavior | Current SQL Behavior | Classification |
|---|---|---|---|
| Numeric scalar types | JSON may use int | SQL/Pydantic emits float for some numeric fields | Intentional |
| Null-equivalent optional fields | Field may exist with null/undefined | Canonical parity may omit absent optional fields | Intentional |
| Order create stock mutation | Decrement stock on sale | Not fully enforced in current service path | Unresolved Gap |
| Order delete stock restore | Restore stock on removal | Not explicitly implemented | Unresolved Gap |
| Register sale reversal | Reversal/removal accepted | Current behavior removes sale transaction | Preserved |

## Legacy Test Rewrites
- Legacy files src/services/database.test.ts and src/services/database.persistence.test.ts are not present in the workspace.
- Mapping has been documented as deferred in Documentation/Legacy_Test_Mapping.md.

## Acceptance Criteria Status
| Criterion | Status |
|---|---|
| integrity_check returns ok | PASS |
| Task 5 row counts match source expectations with quarantine accounting | PASS |
| No failed critical-path scenarios remain | PARTIAL |
| Every dropped or rewritten legacy test has documented reason | PARTIAL |

## Open Gaps
1. Implement explicit stock decrement/restore in order workflow service and strengthen assertions accordingly.
2. Complete legacy test mapping once historical frontend test files are recovered.
3. Add explicit quarantined-record scenario fixture if/when quarantine data exists.

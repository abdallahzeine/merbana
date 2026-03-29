# Legacy Test Mapping (Task 7)

## Current Status
Task 7 requested classification for:
- src/services/database.test.ts
- src/services/database.persistence.test.ts

These files are not present in the current workspace snapshot.

## Decision
Classification is deferred until the legacy files are recovered from history or another branch.

## Interim Mapping Approach Used
Current backend-focused replacement coverage was added in backend/tests:
- API coverage by entity route
- workflow and integrity suites
- migration parity and artifact validation

## Provisional Categories
| Legacy Target | Classification | Rationale |
|---|---|---|
| src/services/database.test.ts | Deferred | Source file unavailable for line-by-line mapping |
| src/services/database.persistence.test.ts | Deferred | Source file unavailable for line-by-line mapping |

## Follow-up Required
1. Recover legacy files from git history.
2. Produce explicit per-test mapping: portable, rewrite-required, obsolete, replaced-by-backend-test.
3. Link each retired test to a replacement backend test or documented intentional removal.

# 02 Shared Test Utils

## Goal
Create reusable utilities for live API tests to keep suites small and deterministic.

## Target Files
- `src/api/__tests__/helpers/liveApi.ts`
- `src/api/__tests__/helpers/factories.ts`
- `src/api/__tests__/helpers/assertions.ts`

## Utilities To Implement
- Timestamped ID generator.
- Entity payload factories (user/category/product/order).
- Common assertions for list shape and numeric totals.
- Safe cleanup helpers tolerant to already-deleted entities.

## Checklist
- [ ] Add helper module structure.
- [ ] Add payload factory methods used across suites.
- [ ] Add assertion helpers with readable failure messages.
- [ ] Add shared constants for backend URL and test timeout.

## Done Criteria
- All suites can import helpers instead of duplicating setup.
- Failure output is clear and includes entity ID context.

# 05 Products CRUD T15-T22

## Goal
Implement products basic CRUD tests T15-T22.

## Test File
- `src/api/__tests__/productsApi.test.ts` (CRUD block)

## Test Coverage
- T15 Create simple product.
- T16 Fetch all products.
- T17 Fetch single product.
- T18 Update name.
- T19 Update price.
- T20 Increase stock.
- T21 Decrease stock.
- T22 Delete product.

## Checklist
- [ ] Create prerequisite category in setup.
- [ ] Verify create/fetch/update field integrity.
- [ ] Validate stock deltas and persistence after refetch.
- [ ] Validate delete behavior and absence from list.
- [ ] Capture endpoint mismatch behavior for stock path if encountered.

## Run Command
- `npm run test -- src/api/__tests__/productsApi.test.ts`

## Done Criteria
- CRUD block T15-T22 passes, including stock adjustments.

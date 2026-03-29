# 07 Products Stock T28-T32

## Goal
Implement stock management and workflow tests T28-T32.

## Test File
- `src/api/__tests__/productsApi.test.ts` (stock and workflow blocks)

## Test Coverage
- T28 Create product with stock tracking.
- T29 Verify stock increase.
- T30 Verify stock decrease.
- T31 Bulk stock update.
- T32 Full product workflow integration.

## Checklist
- [ ] Create stock-tracked products with known starting quantities.
- [ ] Verify adjust stock positive and negative deltas.
- [ ] Verify bulk stock updates for multiple products.
- [ ] Implement full workflow checks for persistence of all updates.
- [ ] Record any backend/client stock endpoint incompatibility.

## Run Command
- `npm run test -- src/api/__tests__/productsApi.test.ts`

## Done Criteria
- T28-T32 pass with deterministic expected stock values.

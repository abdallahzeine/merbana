# 06 Products Sizes T23-T27

## Goal
Implement product size/options tests T23-T27.

## Test File
- `src/api/__tests__/productsApi.test.ts` (sizes block)

## Test Coverage
- T23 Create product with sizes.
- T24 Verify sizes returned.
- T25 Add size.
- T26 Remove size.
- T27 Update size price.

## Checklist
- [ ] Create product with 2 deterministic sizes.
- [ ] Verify `name`, `price`, `sortOrder` for each size.
- [ ] Update sizes array with add/remove operations.
- [ ] Verify final sizes array exactly matches expected state.
- [ ] Verify no accidental product field regressions during size updates.

## Run Command
- `npm run test -- src/api/__tests__/productsApi.test.ts`

## Done Criteria
- T23-T27 pass and preserve consistent size ordering.

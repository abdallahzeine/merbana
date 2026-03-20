# 08 Orders Read T33-T35

## Goal
Implement orders read tests T33-T35.

## Test File
- `src/api/__tests__/ordersApi.test.ts` (read block)

## Test Coverage
- T33 Get next order number.
- T34 Fetch orders with pagination.
- T35 Fetch single order.

## Checklist
- [ ] Validate next order number response shape.
- [ ] Validate list response (`data`, optional `total`, pagination behavior).
- [ ] Create or reuse known order fixture for single fetch assertion.
- [ ] Verify field presence and type expectations on fetched order.

## Run Command
- `npm run test -- src/api/__tests__/ordersApi.test.ts`

## Done Criteria
- T33-T35 pass against live backend with stable assertions.

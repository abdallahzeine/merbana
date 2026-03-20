# 09 Orders Create/Delete T36-T44

## Goal
Implement order create variants and delete verification tests T36-T44.

## Test File
- `src/api/__tests__/ordersApi.test.ts` (create/delete block)

## Test Coverage
- T36 cash + dine_in.
- T37 shamcash variant.
- T38 takeaway variant.
- T39 multiple items totals.
- T40 item with size.
- T41 order note.
- T42 verify persisted order fields.
- T43 delete order.
- T44 full order verification.

## Checklist
- [ ] Build reusable order item factory with explicit subtotal math.
- [ ] Verify `total` equals sum of item subtotals.
- [ ] Verify payment and order type variants.
- [ ] Verify note and size persistence.
- [ ] Verify delete behavior and not-found or list absence after deletion.

## Run Command
- `npm run test -- src/api/__tests__/ordersApi.test.ts`

## Done Criteria
- T36-T44 pass and expose any subtotal/order-number backend issues clearly.

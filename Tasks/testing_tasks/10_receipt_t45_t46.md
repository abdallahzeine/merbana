# 10 Receipt T45-T46

## Goal
Implement receipt data validation tests T45-T46 from live order + settings data.

## Test File
- `src/api/__tests__/receiptData.test.ts`

## Test Coverage
- T45 Receipt data structure.
- T46 Receipt variation coverage (multiple items, sizes, note, payment variants).

## Checklist
- [ ] Create order fixture with known values and fetch settings.
- [ ] Map order to receipt structure under test.
- [ ] Validate company name, order number formatting, date, items, totals, footer.
- [ ] Validate optional note and size display fields.

## Run Command
- `npm run test -- src/api/__tests__/receiptData.test.ts`

## Done Criteria
- T45-T46 pass with deterministic receipt mapping assertions.

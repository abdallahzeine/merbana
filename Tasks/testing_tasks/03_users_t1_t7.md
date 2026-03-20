# 03 Users T1-T7

## Goal
Implement and pass users API tests T1-T7 against live backend.

## Test File
- `src/api/__tests__/usersApi.test.ts`

## Test Coverage
- T1 Create user without password.
- T2 Create user with password.
- T3 Fetch all users.
- T4 Verify created user in list.
- T5 Update user name.
- T6 Update user password.
- T7 Delete user.

## Checklist
- [ ] Create suite with deterministic ID naming.
- [ ] Verify `hasPassword` behavior for both create paths.
- [ ] Verify update responses and persisted values via refetch.
- [ ] Verify delete returns void behavior and user no longer listed.
- [ ] Add cleanup safety for partial failures.

## Run Command
- `npm run test -- src/api/__tests__/usersApi.test.ts`

## Done Criteria
- T1-T7 pass consistently on repeated runs.

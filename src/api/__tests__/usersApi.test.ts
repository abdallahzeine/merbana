// @vitest-environment node

import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';
import { assertListShape, assertNumericTotal } from './helpers/assertions';
import { buildUserPayload } from './helpers/factories';
import {
  assertLiveBackendReachable,
  configureLiveApiSuite,
  LIVE_TEST_TIMEOUT_MS,
  safeDeleteById,
  teardownLiveApiSuite,
} from './helpers/liveApi';

interface UsersApiModule {
  fetchUsers: () => Promise<{ data: Array<{ id: string; name: string; password?: string | null; createdAt: string }>; total?: number | null }>;
  createUser: (data: { id: string; name: string; password?: string; createdAt: string }) => Promise<{ id: string; name: string; password?: string | null; createdAt: string }>;
  updateUser: (id: string, data: { name?: string; password?: string }) => Promise<{ id: string; name: string; password?: string | null; createdAt: string }>;
  deleteUser: (id: string) => Promise<void>;
}

describe('usersApi live backend T1-T7', () => {
  let usersApi: UsersApiModule;
  const createdUserIds = new Set<string>();

  let noPasswordUserId = '';
  let withPasswordUserId = '';

  beforeAll(async () => {
    configureLiveApiSuite();
    await assertLiveBackendReachable();

    vi.resetModules();
    usersApi = (await import('../usersApi')) as UsersApiModule;
  }, LIVE_TEST_TIMEOUT_MS);

  afterAll(async () => {
    for (const userId of createdUserIds) {
      await safeDeleteById('user', userId, usersApi.deleteUser);
    }
    teardownLiveApiSuite();
  }, LIVE_TEST_TIMEOUT_MS);

  it('T1 Create user without password', async () => {
    const payload = buildUserPayload('t1-user-no-password', false);
    const created = await usersApi.createUser(payload);

    noPasswordUserId = created.id;
    createdUserIds.add(created.id);

    expect(created.id).toBe(payload.id);
    expect(created.name).toBe(payload.name);
    expect(created.createdAt).toBe(payload.createdAt);
    expect(created.password ?? null).toBeNull();
    expect(Boolean(created.password), 'hasPassword should be false').toBe(false);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T2 Create user with password', async () => {
    const payload = buildUserPayload('t2-user-with-password', true);
    const created = await usersApi.createUser(payload);

    withPasswordUserId = created.id;
    createdUserIds.add(created.id);

    expect(created.id).toBe(payload.id);
    expect(created.name).toBe(payload.name);
    expect(created.createdAt).toBe(payload.createdAt);
    expect(created.password).toBe(payload.password);
    expect(Boolean(created.password), 'hasPassword should be true').toBe(true);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T3 Fetch all users', async () => {
    const list = await usersApi.fetchUsers();

    assertListShape(list, 'users');
    assertNumericTotal(list, 'users');
  }, LIVE_TEST_TIMEOUT_MS);

  it('T4 Verify created users in list', async () => {
    const list = await usersApi.fetchUsers();

    const noPasswordUser = list.data.find((user) => user.id === noPasswordUserId);
    const withPasswordUser = list.data.find((user) => user.id === withPasswordUserId);

    expect(noPasswordUser, `created user ${noPasswordUserId} should exist`).toBeDefined();
    expect(withPasswordUser, `created user ${withPasswordUserId} should exist`).toBeDefined();

    expect(Boolean(noPasswordUser?.password), 'hasPassword should be false').toBe(false);
    expect(Boolean(withPasswordUser?.password), 'hasPassword should be true').toBe(true);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T5 Update user name', async () => {
    const updatedName = `updated-${Date.now()}`;

    const updated = await usersApi.updateUser(noPasswordUserId, {
      name: updatedName,
    });

    expect(updated.id).toBe(noPasswordUserId);
    expect(updated.name).toBe(updatedName);

    const list = await usersApi.fetchUsers();
    const persisted = list.data.find((user) => user.id === noPasswordUserId);

    expect(persisted).toBeDefined();
    expect(persisted?.name).toBe(updatedName);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T6 Update user password', async () => {
    const newPassword = `new-pass-${Date.now()}`;

    const updated = await usersApi.updateUser(noPasswordUserId, {
      password: newPassword,
    });

    expect(updated.id).toBe(noPasswordUserId);
    expect(updated.password).toBe(newPassword);
    expect(Boolean(updated.password), 'hasPassword should be true').toBe(true);

    const list = await usersApi.fetchUsers();
    const persisted = list.data.find((user) => user.id === noPasswordUserId);

    expect(persisted).toBeDefined();
    expect(persisted?.password).toBe(newPassword);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T7 Delete user', async () => {
    const result = await usersApi.deleteUser(withPasswordUserId);

    expect(result).toBeUndefined();
    createdUserIds.delete(withPasswordUserId);

    const list = await usersApi.fetchUsers();
    const deleted = list.data.find((user) => user.id === withPasswordUserId);

    expect(deleted, `deleted user ${withPasswordUserId} should be absent`).toBeUndefined();
  }, LIVE_TEST_TIMEOUT_MS);
});

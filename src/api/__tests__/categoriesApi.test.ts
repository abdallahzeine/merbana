// @vitest-environment node

import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';
import {
  assertCategoryFields,
  assertListShape,
  assertNumericTotal,
} from './helpers/assertions';
import { buildCategoryPayload } from './helpers/factories';
import {
  assertLiveBackendReachable,
  configureLiveApiSuite,
  LIVE_TEST_TIMEOUT_MS,
  safeDeleteById,
  teardownLiveApiSuite,
} from './helpers/liveApi';

interface CategoriesApiModule {
  fetchCategories: () => Promise<{ data: Array<{ id: string; name: string; productCount: number }>; total?: number | null }>;
  createCategory: (id: string, name: string) => Promise<{ id: string; name: string }>;
  deleteCategory: (id: string) => Promise<void>;
}

describe('categoriesApi live backend T11-T14', () => {
  let categoriesApi: CategoriesApiModule;
  const createdCategoryIds = new Set<string>();

  const baselineCategoryIds = new Set<string>();
  let createdBeverageId = '';
  let createdFoodId = '';

  beforeAll(async () => {
    configureLiveApiSuite();
    await assertLiveBackendReachable();

    vi.resetModules();
    categoriesApi = (await import('../categoriesApi')) as CategoriesApiModule;

    const initial = await categoriesApi.fetchCategories();
    for (const category of initial.data) {
      baselineCategoryIds.add(category.id);
    }
  }, LIVE_TEST_TIMEOUT_MS);

  afterAll(async () => {
    for (const categoryId of createdCategoryIds) {
      await safeDeleteById('category', categoryId, categoriesApi.deleteCategory);
    }
    teardownLiveApiSuite();
  }, LIVE_TEST_TIMEOUT_MS);

  it('T11 Fetch all categories', async () => {
    const list = await categoriesApi.fetchCategories();

    assertListShape(list, 'categories');
    assertNumericTotal(list, 'categories');
    for (const category of list.data) {
      assertCategoryFields(category);
    }
  }, LIVE_TEST_TIMEOUT_MS);

  it('T12 Create beverage category', async () => {
    const payload = buildCategoryPayload('t12-beverage');
    const created = await categoriesApi.createCategory(payload.id, payload.name);

    createdBeverageId = created.id;
    createdCategoryIds.add(created.id);

    expect(created).toEqual({
      id: payload.id,
      name: payload.name,
    });
  }, LIVE_TEST_TIMEOUT_MS);

  it('T13 Create food category', async () => {
    const payload = buildCategoryPayload('t13-food');
    const created = await categoriesApi.createCategory(payload.id, payload.name);

    createdFoodId = created.id;
    createdCategoryIds.add(created.id);

    expect(created).toEqual({
      id: payload.id,
      name: payload.name,
    });
  }, LIVE_TEST_TIMEOUT_MS);

  it('T14 Delete empty category', async () => {
    const result = await categoriesApi.deleteCategory(createdFoodId);

    expect(result).toBeUndefined();
    createdCategoryIds.delete(createdFoodId);

    const list = await categoriesApi.fetchCategories();
    const deleted = list.data.find((category) => category.id === createdFoodId);
    const remainingCreated = list.data.find(
      (category) => category.id === createdBeverageId,
    );

    expect(deleted, `deleted category ${createdFoodId} should be absent`).toBeUndefined();
    expect(
      remainingCreated,
      `non-deleted created category ${createdBeverageId} should remain`,
    ).toBeDefined();

    const currentIds = new Set(list.data.map((category) => category.id));
    for (const baselineId of baselineCategoryIds) {
      expect(
        currentIds.has(baselineId),
        `baseline category ${baselineId} should still exist`,
      ).toBe(true);
    }
  }, LIVE_TEST_TIMEOUT_MS);
});

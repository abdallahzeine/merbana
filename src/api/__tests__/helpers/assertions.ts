import { expect } from 'vitest';

export function assertListShape<T>(
  list: { data: T[]; total?: number | null },
  entityName: string,
): void {
  expect(Array.isArray(list.data), `${entityName} data must be an array`).toBe(
    true,
  );

  if (list.total !== undefined && list.total !== null) {
    expect(
      typeof list.total,
      `${entityName} total must be numeric when present`,
    ).toBe('number');
  }
}

export function assertNumericTotal(
  list: { total?: number | null },
  entityName: string,
): void {
  if (list.total !== undefined && list.total !== null) {
    expect(
      Number.isFinite(list.total),
      `${entityName} total must be finite`,
    ).toBe(true);
  }
}

export function assertCategoryFields(category: {
  id: string;
  name: string;
  productCount?: number;
}): void {
  expect(category.id, 'category id should be defined').toBeTruthy();
  expect(category.name, 'category name should be defined').toBeTruthy();

  if (category.productCount !== undefined) {
    expect(
      Number.isInteger(category.productCount),
      'category productCount should be an integer',
    ).toBe(true);
    expect(category.productCount, 'category productCount should be numeric').toEqual(
      expect.any(Number),
    );
    expect(category.productCount).toBeGreaterThanOrEqual(0);
  }
}

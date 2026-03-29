// @vitest-environment node

import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';
import { ApiError } from '../client';
import { assertListShape, assertNumericTotal } from './helpers/assertions';
import {
  buildCategoryPayload,
  buildProductPayload,
  createUuid,
} from './helpers/factories';
import {
  assertLiveBackendReachable,
  configureLiveApiSuite,
  LIVE_TEST_TIMEOUT_MS,
  safeDeleteById,
  teardownLiveApiSuite,
} from './helpers/liveApi';

interface OrdersApiModule {
  fetchOrders: (limit?: number, offset?: number) => Promise<{ data: Array<{ id: string; orderNumber?: number; date: string; total: number }>; total?: number | null }>;
  fetchOrder: (id: string) => Promise<{
    id: string;
    orderNumber: number;
    date: string;
    total: number;
    paymentMethod: 'cash' | 'shamcash';
    orderType: 'dine_in' | 'takeaway';
    note?: string;
    items: Array<{
      productId?: string;
      name: string;
      price: number;
      quantity: number;
      size?: string;
      subtotal: number;
    }>;
  }>;
  createOrder: (data: {
    items: Array<{
      productId: string;
      name: string;
      price: number;
      quantity: number;
      size?: string;
      subtotal: number;
    }>;
    paymentMethod: 'cash' | 'shamcash';
    orderType: 'dine_in' | 'takeaway';
    note?: string;
    userId?: string;
    userName?: string;
  }) => Promise<{
    id: string;
    orderNumber: number;
    date: string;
    total: number;
    paymentMethod: 'cash' | 'shamcash';
    orderType: 'dine_in' | 'takeaway';
    note?: string;
    userId?: string;
    userName?: string;
    items: Array<{
      productId?: string;
      name: string;
      price: number;
      quantity: number;
      size?: string;
      subtotal: number;
    }>;
  }>;
  deleteOrder: (id: string) => Promise<void>;
  getNextOrderNumber: () => Promise<{ order_number: number }>;
}

interface CategoriesApiModule {
  createCategory: (id: string, name: string) => Promise<{ id: string; name: string }>;
  deleteCategory: (id: string) => Promise<void>;
}

interface ProductsApiModule {
  createProduct: (data: {
    id: string;
    name: string;
    price: number;
    categoryId?: string;
    stock?: number;
    trackStock?: boolean;
    createdAt: string;
    sizes: Array<{ id: string; name: string; price: number; sortOrder: number }>;
  }) => Promise<{
    id: string;
    name: string;
    price: number;
    categoryId?: string;
    stock?: number;
    trackStock?: boolean;
    createdAt: string;
    sizes: Array<{ id: string; name: string; price: number; sortOrder: number }>;
  }>;
  deleteProduct: (id: string) => Promise<void>;
}

function buildOrderItem(input: {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
}): {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  subtotal: number;
} {
  return {
    productId: input.productId,
    name: input.name,
    price: input.price,
    quantity: input.quantity,
    size: input.size,
    subtotal: input.price * input.quantity,
  };
}

function sumSubtotals(items: Array<{ subtotal: number }>): number {
  return items.reduce((acc, item) => acc + item.subtotal, 0);
}

function isNotFoundError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === 'NOT_FOUND';
  }

  if (error instanceof Error) {
    return /not found|404/i.test(error.message);
  }

  return false;
}

function normalizeOrder(
  order: {
    id: string;
    orderNumber?: number;
    order_number?: number;
    date: string;
    total: number;
    paymentMethod?: 'cash' | 'shamcash';
    payment_method?: 'cash' | 'shamcash';
    orderType?: 'dine_in' | 'takeaway';
    order_type?: 'dine_in' | 'takeaway';
    note?: string | null;
    userId?: string;
    user_id?: string;
    userName?: string;
    user_name?: string;
    items: Array<{
      productId?: string;
      product_id?: string | null;
      name: string;
      price: number;
      quantity: number;
      size?: string | null;
      subtotal: number;
    }>;
  },
): {
  id: string;
  orderNumber: number;
  date: string;
  total: number;
  paymentMethod: 'cash' | 'shamcash';
  orderType: 'dine_in' | 'takeaway';
  note?: string;
  userId?: string;
  userName?: string;
  items: Array<{
    productId?: string;
    name: string;
    price: number;
    quantity: number;
    size?: string;
    subtotal: number;
  }>;
} {
  return {
    id: order.id,
    orderNumber: order.orderNumber ?? (order.order_number as number),
    date: order.date,
    total: order.total,
    paymentMethod: order.paymentMethod ?? (order.payment_method as 'cash' | 'shamcash'),
    orderType: order.orderType ?? (order.order_type as 'dine_in' | 'takeaway'),
    note: order.note ?? undefined,
    userId: order.userId ?? order.user_id ?? undefined,
    userName: order.userName ?? order.user_name ?? undefined,
    items: order.items.map((item) => ({
      productId: item.productId ?? item.product_id ?? undefined,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      size: item.size ?? undefined,
      subtotal: item.subtotal,
    })),
  };
}

describe('ordersApi live backend T33-T44', () => {
  let ordersApi: OrdersApiModule;
  let categoriesApi: CategoriesApiModule;
  let productsApi: ProductsApiModule;

  const createdOrderIds = new Set<string>();
  const createdCategoryIds = new Set<string>();
  const createdProductIds = new Set<string>();

  let categoryId = '';
  let productAId = '';
  let productBId = '';

  let fixtureOrderId = '';
  let shamcashOrderId = '';
  let takeawayOrderId = '';
  let multiItemOrderId = '';
  let sizeOrderId = '';
  let noteOrderId = '';
  let persistenceOrderId = '';
  let deletedOrderId = '';
  let fullVerifyOrderId = '';

  beforeAll(async () => {
    configureLiveApiSuite();
    await assertLiveBackendReachable();

    vi.resetModules();
    ordersApi = (await import('../ordersApi')) as OrdersApiModule;
    categoriesApi = (await import('../categoriesApi')) as CategoriesApiModule;
    productsApi = (await import('../productsApi')) as ProductsApiModule;

    const categoryPayload = buildCategoryPayload('orders-api-prereq-category');
    const category = await categoriesApi.createCategory(
      categoryPayload.id,
      categoryPayload.name,
    );
    categoryId = category.id;
    createdCategoryIds.add(category.id);

    const productA = await productsApi.createProduct({
      ...buildProductPayload({
        namePrefix: 'orders-api-product-a',
        categoryId,
        price: 10,
      }),
      stock: 200,
      trackStock: true,
      sizes: [],
    });
    productAId = productA.id;
    createdProductIds.add(productA.id);

    const productB = await productsApi.createProduct({
      ...buildProductPayload({
        namePrefix: 'orders-api-product-b',
        categoryId,
        price: 20,
      }),
      stock: 200,
      trackStock: true,
      sizes: [
        { id: createUuid(), name: 'Medium', price: 22, sortOrder: 1 },
        { id: createUuid(), name: 'Large', price: 25, sortOrder: 2 },
      ],
    });
    productBId = productB.id;
    createdProductIds.add(productB.id);
  }, LIVE_TEST_TIMEOUT_MS);

  afterAll(async () => {
    for (const orderId of createdOrderIds) {
      await safeDeleteById('order', orderId, ordersApi.deleteOrder);
    }

    for (const productId of createdProductIds) {
      await safeDeleteById('product', productId, productsApi.deleteProduct);
    }

    for (const cleanupCategoryId of createdCategoryIds) {
      await safeDeleteById('category', cleanupCategoryId, categoriesApi.deleteCategory);
    }

    teardownLiveApiSuite();
  }, LIVE_TEST_TIMEOUT_MS);

  it('T33 Get next order number', async () => {
    const next = await ordersApi.getNextOrderNumber();

    expect(next).toHaveProperty('order_number');
    expect(Number.isInteger(next.order_number)).toBe(true);
    expect(next.order_number).toBeGreaterThanOrEqual(1);
    expect(next.order_number).toBeLessThanOrEqual(100);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T34 Fetch orders with pagination', async () => {
    const list = await ordersApi.fetchOrders(3, 0);

    assertListShape(list, 'orders');
    assertNumericTotal(list, 'orders');
    expect(list.data.length).toBeLessThanOrEqual(3);
    for (const summary of list.data) {
      expect(typeof summary.id).toBe('string');
      expect(typeof summary.total).toBe('number');
      expect(summary.date).toBeTruthy();
    }
  }, LIVE_TEST_TIMEOUT_MS);

  it('T35 Fetch single order', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T35 Item',
        price: 10,
        quantity: 2,
      }),
    ];
    const createdRaw = await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
    });
    const created = normalizeOrder(createdRaw);

    fixtureOrderId = created.id;
    createdOrderIds.add(created.id);

    const fetched = normalizeOrder(await ordersApi.fetchOrder(fixtureOrderId));
    expect(fetched.id).toBe(fixtureOrderId);
    expect(typeof fetched.orderNumber).toBe('number');
    expect(fetched.paymentMethod).toBe('cash');
    expect(fetched.orderType).toBe('dine_in');
    expect(Array.isArray(fetched.items)).toBe(true);
    expect(fetched.items.length).toBe(1);
    expect(fetched.items[0]).toMatchObject({
      productId: productAId,
      name: 'T35 Item',
      price: 10,
      quantity: 2,
      subtotal: 20,
    });
    expect(fetched.total).toBe(sumSubtotals(items));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T36 Create order cash + dine_in', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T36 Cash DineIn',
        price: 11,
        quantity: 1,
      }),
    ];
    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
      userName: 'T36 Runner',
    }));

    createdOrderIds.add(created.id);

    expect(created.paymentMethod).toBe('cash');
    expect(created.orderType).toBe('dine_in');
    expect(created.total).toBe(sumSubtotals(items));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T37 Create order shamcash variant', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T37 ShamCash',
        price: 13,
        quantity: 2,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'shamcash',
      orderType: 'dine_in',
      items,
    }));

    shamcashOrderId = created.id;
    createdOrderIds.add(created.id);

    expect(created.paymentMethod).toBe('shamcash');
    expect(created.orderType).toBe('dine_in');
    expect(created.total).toBe(sumSubtotals(items));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T38 Create order takeaway variant', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T38 Takeaway',
        price: 9,
        quantity: 3,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'takeaway',
      items,
    }));

    takeawayOrderId = created.id;
    createdOrderIds.add(created.id);

    expect(created.paymentMethod).toBe('cash');
    expect(created.orderType).toBe('takeaway');
    expect(created.total).toBe(sumSubtotals(items));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T39 Create order multiple items totals', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T39 Item A',
        price: 7,
        quantity: 4,
      }),
      buildOrderItem({
        productId: productBId,
        name: 'T39 Item B',
        price: 21,
        quantity: 1,
      }),
    ];
    const expectedTotal = sumSubtotals(items);

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
    }));

    multiItemOrderId = created.id;
    createdOrderIds.add(created.id);

    expect(created.items.length).toBe(2);
    expect(created.total).toBe(expectedTotal);
    expect(created.total).toBe(created.items.reduce((sum, item) => sum + item.subtotal, 0));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T40 Create order item with size', async () => {
    const sizeLabel = 'Large';
    const items = [
      buildOrderItem({
        productId: productBId,
        name: 'T40 Item Sized',
        price: 25,
        quantity: 2,
        size: sizeLabel,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
    }));

    sizeOrderId = created.id;
    createdOrderIds.add(created.id);

    expect(created.items[0].size).toBe(sizeLabel);
    expect(created.total).toBe(50);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T41 Create order note', async () => {
    const note = 'No onion please';
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T41 Note Item',
        price: 8,
        quantity: 2,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      note,
      items,
    }));

    noteOrderId = created.id;
    createdOrderIds.add(created.id);

    expect(created.note).toBe(note);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T42 Verify persisted order fields', async () => {
    const expectedNote = 'Persist fields check';
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T42 Persisted A',
        price: 12,
        quantity: 1,
      }),
      buildOrderItem({
        productId: productBId,
        name: 'T42 Persisted B',
        price: 22,
        quantity: 2,
        size: 'Medium',
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'shamcash',
      orderType: 'takeaway',
      note: expectedNote,
      items,
      userName: 'T42 User',
    }));

    persistenceOrderId = created.id;
    createdOrderIds.add(created.id);

    const fetched = normalizeOrder(await ordersApi.fetchOrder(persistenceOrderId));
    expect(fetched.id).toBe(created.id);
    expect(fetched.orderNumber).toBe(created.orderNumber);
    expect(fetched.paymentMethod).toBe('shamcash');
    expect(fetched.orderType).toBe('takeaway');
    expect(fetched.note).toBe(expectedNote);
    expect(fetched.items).toHaveLength(2);
    expect(fetched.items[1].size).toBe('Medium');
    expect(fetched.total).toBe(sumSubtotals(items));
  }, LIVE_TEST_TIMEOUT_MS);

  it('T43 Delete order', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T43 Delete Target',
        price: 10,
        quantity: 1,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
    }));

    deletedOrderId = created.id;
    createdOrderIds.add(created.id);

    await ordersApi.deleteOrder(deletedOrderId);
    createdOrderIds.delete(deletedOrderId);

    await expect(ordersApi.fetchOrder(deletedOrderId)).rejects.toSatisfy(isNotFoundError);

    const list = await ordersApi.fetchOrders(1000, 0);
    const stillPresent = list.data.some((order) => order.id === deletedOrderId);
    expect(stillPresent).toBe(false);
  }, LIVE_TEST_TIMEOUT_MS);

  it('T44 Full order verification', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T44 Full A',
        price: 14,
        quantity: 2,
      }),
      buildOrderItem({
        productId: productBId,
        name: 'T44 Full B',
        price: 25,
        quantity: 1,
        size: 'Large',
      }),
    ];
    const expectedTotal = sumSubtotals(items);

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'shamcash',
      orderType: 'takeaway',
      note: 'T44 final verification',
      items,
      userName: 'T44 Operator',
    }));

    fullVerifyOrderId = created.id;
    createdOrderIds.add(created.id);

    const fetched = normalizeOrder(await ordersApi.fetchOrder(fullVerifyOrderId));
    expect(fetched.id).toBe(created.id);
    expect(fetched.orderNumber).toBe(created.orderNumber);
    expect(fetched.paymentMethod).toBe('shamcash');
    expect(fetched.orderType).toBe('takeaway');
    expect(fetched.note).toBe('T44 final verification');
    expect(fetched.items).toHaveLength(2);
    expect(fetched.items[0]).toMatchObject({
      productId: productAId,
      name: 'T44 Full A',
      price: 14,
      quantity: 2,
      subtotal: 28,
    });
    expect(fetched.items[1]).toMatchObject({
      productId: productBId,
      name: 'T44 Full B',
      price: 25,
      quantity: 1,
      size: 'Large',
      subtotal: 25,
    });
    expect(fetched.total).toBe(expectedTotal);

    // Ensure variant scenario IDs are populated by their respective test cases.
    expect(shamcashOrderId).toMatch(/^[0-9a-f-]{36}$/);
    expect(takeawayOrderId).toMatch(/^[0-9a-f-]{36}$/);
    expect(multiItemOrderId).toMatch(/^[0-9a-f-]{36}$/);
    expect(sizeOrderId).toMatch(/^[0-9a-f-]{36}$/);
    expect(noteOrderId).toMatch(/^[0-9a-f-]{36}$/);
  }, LIVE_TEST_TIMEOUT_MS);
});
// @vitest-environment node

import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest';
import { formatCurrency, formatDateTime } from '../../utils/formatters';
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
}

interface SettingsApiModule {
  fetchSettings: () => Promise<{ companyName: string }>;
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
  }) => Promise<{ id: string }>;
  deleteProduct: (id: string) => Promise<void>;
}

type ReceiptData = {
  companyName: string;
  orderLabel: string;
  dateLabel: string;
  paymentLabel: 'ShamCash' | 'نقدي';
  orderTypeLabel: 'صالة' | 'سفري';
  items: Array<{
    name: string;
    quantity: number;
    price: number;
    subtotal: number;
    sizeLabel: string | null;
  }>;
  totals: {
    grandTotal: string;
    numericTotal: number;
  };
  note: string | null;
  footer: string;
};

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

function mapOrderToReceiptData(input: {
  companyName: string;
  order: {
    orderNumber: number;
    date: string;
    total: number;
    paymentMethod: 'cash' | 'shamcash';
    orderType: 'dine_in' | 'takeaway';
    note?: string;
    items: Array<{
      name: string;
      quantity: number;
      price: number;
      subtotal: number;
      size?: string;
    }>;
  };
}): ReceiptData {
  return {
    companyName: input.companyName,
    orderLabel: `طلب #${String(input.order.orderNumber).padStart(3, '0')}`,
    dateLabel: formatDateTime(input.order.date),
    paymentLabel: input.order.paymentMethod === 'shamcash' ? 'ShamCash' : 'نقدي',
    orderTypeLabel: input.order.orderType === 'dine_in' ? 'صالة' : 'سفري',
    items: input.order.items.map((item) => ({
      name: item.name,
      quantity: item.quantity,
      price: item.price,
      subtotal: item.subtotal,
      sizeLabel: item.size ?? null,
    })),
    totals: {
      grandTotal: formatCurrency(input.order.total),
      numericTotal: input.order.total,
    },
    note: input.order.note ?? null,
    footer: 'شكراً لتعاملكم معنا!',
  };
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
    items: Array<{
      name: string;
      quantity: number;
      price: number;
      subtotal: number;
      size?: string | null;
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
  items: Array<{
    name: string;
    quantity: number;
    price: number;
    subtotal: number;
    size?: string;
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
    items: order.items.map((item) => ({
      name: item.name,
      quantity: item.quantity,
      price: item.price,
      subtotal: item.subtotal,
      size: item.size ?? undefined,
    })),
  };
}

describe('receipt data mapping live backend T45-T46', () => {
  let ordersApi: OrdersApiModule;
  let settingsApi: SettingsApiModule;
  let categoriesApi: CategoriesApiModule;
  let productsApi: ProductsApiModule;

  const createdOrderIds = new Set<string>();
  const createdCategoryIds = new Set<string>();
  const createdProductIds = new Set<string>();

  let companyName = '';
  let productAId = '';
  let productBId = '';

  beforeAll(async () => {
    configureLiveApiSuite();
    await assertLiveBackendReachable();

    vi.resetModules();
    ordersApi = (await import('../ordersApi')) as OrdersApiModule;
    settingsApi = (await import('../settingsApi')) as SettingsApiModule;
    categoriesApi = (await import('../categoriesApi')) as CategoriesApiModule;
    productsApi = (await import('../productsApi')) as ProductsApiModule;

    const settings = await settingsApi.fetchSettings();
    companyName = settings.companyName;

    const categoryPayload = buildCategoryPayload('receipt-prereq-category');
    const category = await categoriesApi.createCategory(
      categoryPayload.id,
      categoryPayload.name,
    );
    createdCategoryIds.add(category.id);

    const productA = await productsApi.createProduct({
      ...buildProductPayload({
        namePrefix: 'receipt-product-a',
        categoryId: category.id,
        price: 15,
      }),
      stock: 200,
      trackStock: true,
      sizes: [],
    });
    productAId = productA.id;
    createdProductIds.add(productA.id);

    const productB = await productsApi.createProduct({
      ...buildProductPayload({
        namePrefix: 'receipt-product-b',
        categoryId: category.id,
        price: 30,
      }),
      stock: 200,
      trackStock: true,
      sizes: [
        { id: createUuid(), name: 'Small', price: 30, sortOrder: 1 },
        { id: createUuid(), name: 'Large', price: 35, sortOrder: 2 },
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

    for (const categoryId of createdCategoryIds) {
      await safeDeleteById('category', categoryId, categoriesApi.deleteCategory);
    }

    teardownLiveApiSuite();
  }, LIVE_TEST_TIMEOUT_MS);

  it('T45 Receipt data structure', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T45 Receipt Item',
        price: 15,
        quantity: 2,
      }),
    ];

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'cash',
      orderType: 'dine_in',
      items,
    }));
    createdOrderIds.add(created.id);

    const receipt = mapOrderToReceiptData({
      companyName,
      order: created,
    });

    expect(receipt.companyName).toBe(companyName);
    expect(receipt.orderLabel).toBe(`طلب #${String(created.orderNumber).padStart(3, '0')}`);
    expect(receipt.dateLabel).toBe(formatDateTime(created.date));
    expect(receipt.paymentLabel).toBe('نقدي');
    expect(receipt.orderTypeLabel).toBe('صالة');
    expect(receipt.items).toHaveLength(1);
    expect(receipt.items[0]).toEqual({
      name: 'T45 Receipt Item',
      quantity: 2,
      price: 15,
      subtotal: 30,
      sizeLabel: null,
    });
    expect(receipt.totals.numericTotal).toBe(30);
    expect(receipt.totals.grandTotal).toBe(formatCurrency(30));
    expect(receipt.footer).toBe('شكراً لتعاملكم معنا!');
    expect(receipt.note).toBeNull();
  }, LIVE_TEST_TIMEOUT_MS);

  it('T46 Receipt variation coverage', async () => {
    const items = [
      buildOrderItem({
        productId: productAId,
        name: 'T46 Item One',
        price: 15,
        quantity: 1,
      }),
      buildOrderItem({
        productId: productBId,
        name: 'T46 Item Two',
        price: 35,
        quantity: 2,
        size: 'Large',
      }),
    ];
    const expectedTotal = items.reduce((sum, item) => sum + item.subtotal, 0);

    const created = normalizeOrder(await ordersApi.createOrder({
      paymentMethod: 'shamcash',
      orderType: 'takeaway',
      note: 'Leave at pickup counter',
      items,
      userName: 'T46 Cashier',
    }));
    createdOrderIds.add(created.id);

    const receipt = mapOrderToReceiptData({
      companyName,
      order: created,
    });

    expect(receipt.paymentLabel).toBe('ShamCash');
    expect(receipt.orderTypeLabel).toBe('سفري');
    expect(receipt.items).toHaveLength(2);
    expect(receipt.items[0].sizeLabel).toBeNull();
    expect(receipt.items[1].sizeLabel).toBe('Large');
    expect(receipt.note).toBe('Leave at pickup counter');
    expect(receipt.totals.numericTotal).toBe(expectedTotal);
    expect(receipt.totals.grandTotal).toBe(formatCurrency(expectedTotal));
    expect(receipt.items[1]).toMatchObject({
      name: 'T46 Item Two',
      quantity: 2,
      price: 35,
      subtotal: 70,
    });
  }, LIVE_TEST_TIMEOUT_MS);
});
import { get, post, del } from './client';
import {
  OrderResponse as OrderResponseSchema,
  OrderSummaryListResponse as OrderSummaryListResponseSchema,
} from './schema';
import type { OrderList, Order } from './schema';

function normalizeOrderSummaryList(raw: unknown): OrderList {
  const parsed = OrderSummaryListResponseSchema.parse(raw);
  return {
    total: parsed.total,
    data: parsed.data.map((o) => ({
      id: o.id,
      orderNumber: o.orderNumber,
      date: o.date,
      total: o.total,
    })) as OrderList['data'],
  };
}

export async function fetchOrders(limit = 100, offset = 0): Promise<OrderList> {
  const raw = await get<unknown>('/orders', { limit, offset });
  return normalizeOrderSummaryList(raw);
}

export async function fetchOrder(id: string): Promise<Order> {
  const raw = await get<unknown>(`/orders/${id}`);
  return OrderResponseSchema.parse(raw);
}

export async function createOrder(data: {
  items: { productId: string; name: string; price: number; quantity: number; size?: string; subtotal: number }[];
  paymentMethod: 'cash' | 'shamcash';
  orderType: 'dine_in' | 'takeaway';
  note?: string;
  userId?: string;
  userName?: string;
}): Promise<Order> {
  const body = {
    items: data.items.map(i => ({
      product_id: i.productId,
      name: i.name,
      price: i.price,
      quantity: i.quantity,
      size: i.size ?? null,
      subtotal: i.subtotal,
    })),
    payment_method: data.paymentMethod,
    order_type: data.orderType,
    note: data.note ?? null,
    user_id: data.userId ?? null,
    user_name: data.userName ?? null,
  };
  const raw = await post<unknown>('/orders', body);
  return OrderResponseSchema.parse(raw);
}

export async function deleteOrder(id: string): Promise<void> {
  return del<void>(`/orders/${id}`);
}

export async function getNextOrderNumber(): Promise<{ order_number: number }> {
  return get<{ order_number: number }>('/orders/next-number');
}

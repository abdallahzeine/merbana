export function createTimestampScope(prefix: string): string {
  const compactIso = new Date().toISOString().replace(/[.:]/g, '-');
  const suffix = Math.random().toString(36).slice(2, 8);
  return `${prefix}-${compactIso}-${suffix}`;
}

export function createUuid(): string {
  return crypto.randomUUID();
}

export function buildUserPayload(namePrefix: string, withPassword: boolean): {
  id: string;
  name: string;
  password?: string;
  createdAt: string;
} {
  const unique = createTimestampScope(namePrefix);
  return {
    id: createUuid(),
    name: `${namePrefix}-${unique}`,
    password: withPassword ? `pw-${unique}` : undefined,
    createdAt: new Date().toISOString(),
  };
}

export function buildCategoryPayload(namePrefix: string): {
  id: string;
  name: string;
} {
  const unique = createTimestampScope(namePrefix);
  return {
    id: createUuid(),
    name: `${namePrefix}-${unique}`,
  };
}

export function buildProductPayload(input: {
  namePrefix: string;
  categoryId?: string;
  price?: number;
}): {
  id: string;
  name: string;
  price: number;
  categoryId?: string;
  createdAt: string;
} {
  const unique = createTimestampScope(input.namePrefix);
  return {
    id: createUuid(),
    name: `${input.namePrefix}-${unique}`,
    price: input.price ?? 1,
    categoryId: input.categoryId,
    createdAt: new Date().toISOString(),
  };
}

export function buildOrderPayload(input: {
  productId: string;
  productName: string;
  price?: number;
  quantity?: number;
}): {
  paymentMethod: 'cash' | 'shamcash';
  orderType: 'dine_in' | 'takeaway';
  items: Array<{
    productId: string;
    name: string;
    price: number;
    quantity: number;
    subtotal: number;
  }>;
} {
  const price = input.price ?? 1;
  const quantity = input.quantity ?? 1;

  return {
    paymentMethod: 'cash',
    orderType: 'dine_in',
    items: [
      {
        productId: input.productId,
        name: input.productName,
        price,
        quantity,
        subtotal: price * quantity,
      },
    ],
  };
}

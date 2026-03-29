import { http, HttpResponse } from 'msw';
import type { 
  Product, 
  Order, 
  Category, 
  Debtor, 
  StoreUser, 
  ActivityLog,
  StoreSettings,
  RegisterState,
  CashTransaction
} from '../../types/types';
import { v4 as uuidv4 } from 'uuid';

// Generate valid UUIDs for testing
const generateUUID = () => uuidv4();

interface OrderRequestBody {
  items: Array<{
    product_id: string;
    name: string;
    price: number;
    quantity: number;
    size: string | null;
    subtotal: number;
  }>;
  payment_method: 'cash' | 'shamcash';
  order_type: 'dine_in' | 'takeaway';
  note: string | null;
  user_id: string | null;
  user_name: string | null;
}

function transformOrder(order: Order): Record<string, unknown> {
  return {
    id: order.id,
    order_number: order.orderNumber,
    date: order.date,
    total: order.total,
    payment_method: order.paymentMethod,
    order_type: order.orderType,
    note: order.note || null,
    user_id: order.userId || null,
    user_name: order.userName || null,
    items: order.items.map(item => ({
      id: uuidv4(),
      order_id: order.id,
      product_id: item.productId || null,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      size: item.size || null,
      subtotal: item.subtotal,
    })),
  };
}

function snakeToCamelOrder(body: OrderRequestBody): Order {
  return {
    id: generateUUID(),
    orderNumber: 1002,
    date: new Date().toISOString(),
    items: body.items.map(item => ({
      productId: item.product_id,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      size: item.size || undefined,
      subtotal: item.subtotal,
    })),
    total: body.items.reduce((sum, item) => sum + item.subtotal, 0),
    paymentMethod: body.payment_method,
    orderType: body.order_type,
    note: body.note || undefined,
    userId: body.user_id || undefined,
    userName: body.user_name || undefined,
  };
}

export const mockUsers: StoreUser[] = [
  {
    id: generateUUID(),
    name: 'Admin User',
    createdAt: new Date().toISOString(),
  },
  {
    id: generateUUID(),
    name: 'Cashier User',
    createdAt: new Date().toISOString(),
  },
];

export const mockCategories: Category[] = [
  { id: generateUUID(), name: 'Beverages' },
  { id: generateUUID(), name: 'Food' },
];

export const mockProducts: Product[] = [
  {
    id: generateUUID(),
    name: 'Coffee',
    price: 5.99,
    categoryId: mockCategories[0].id,
    createdAt: new Date().toISOString(),
  },
  {
    id: generateUUID(),
    name: 'Sandwich',
    price: 8.50,
    categoryId: mockCategories[1].id,
    createdAt: new Date().toISOString(),
  },
];

export const mockOrders: Order[] = [
  {
    id: generateUUID(),
    orderNumber: 1001,
    date: new Date().toISOString(),
    items: [
      {
        productId: mockProducts[0].id,
        name: 'Coffee',
        quantity: 2,
        price: 5.99,
        subtotal: 11.98,
      },
    ],
    total: 11.98,
    paymentMethod: 'cash',
    orderType: 'dine_in',
    userId: mockUsers[1].id,
    userName: 'Cashier User',
  },
];

export const mockDebtors: Debtor[] = [
  {
    id: generateUUID(),
    name: 'John Doe',
    amount: 100.00,
    createdAt: new Date().toISOString(),
  },
];

export const mockTransactions: CashTransaction[] = [
  {
    id: generateUUID(),
    type: 'sale',
    amount: 50.00,
    date: new Date().toISOString(),
    orderId: mockOrders[0].id,
    userId: mockUsers[1].id,
  },
];

export const mockRegister: RegisterState = {
  currentBalance: 150.00,
  transactions: mockTransactions,
};

export const mockActivityLogs: ActivityLog[] = [
  {
    id: generateUUID(),
    userId: mockUsers[1].id,
    userName: 'Cashier User',
    action: 'create_order',
    timestamp: new Date().toISOString(),
  },
];

export const mockSettings: StoreSettings = {
  companyName: 'Test Store',
  security: {
    passwordRequiredFor: {
      create_order: false,
      delete_order: true,
      deposit_cash: true,
      withdraw_cash: true,
      close_shift: true,
      add_debtor: false,
      mark_debtor_paid: true,
      delete_debtor: true,
      import_database: true,
    },
  },
};

export const handlers = [
  // Test endpoints for client tests
  http.get('/api/test', () => {
    return HttpResponse.json({ message: 'GET success' });
  }),

  http.post('/api/test', async () => {
    return HttpResponse.json({ id: 'test-id' });
  }),

  http.put('/api/test', async () => {
    return HttpResponse.json({ updated: true });
  }),

  http.patch('/api/test', async () => {
    return HttpResponse.json({ patched: true });
  }),

  http.delete('/api/test', () => {
    return HttpResponse.json({ success: true });
  }),

  // Auth endpoints
  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as { name: string; password: string };
    if (body.name === 'admin' && body.password === 'password') {
      return HttpResponse.json({ user: mockUsers[0], token: 'mock-token' });
    }
    return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 });
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json({ success: true });
  }),

  http.get('/api/auth/me', () => {
    return HttpResponse.json({ user: mockUsers[0] });
  }),

  // Users endpoints
  http.get('/api/users', () => {
    return HttpResponse.json({ 
      data: mockUsers.map(u => ({
        id: u.id,
        name: u.name,
        created_at: u.createdAt,
      })),
    });
  }),

  http.delete('/api/users/:id', () => {
    return HttpResponse.json({ success: true });
  }),

  // Products endpoints
  http.get('/api/products', () => {
    return HttpResponse.json({ 
      data: mockProducts.map(p => ({
        ...p,
        category_id: p.categoryId,
        created_at: p.createdAt,
        sizes: p.sizes || [],
      })),
      total: mockProducts.length,
    });
  }),

  http.get('/api/products/:id', ({ params }) => {
    const product = mockProducts.find((p) => p.id === params.id);
    if (product) {
      return HttpResponse.json({
        ...product,
        category_id: product.categoryId,
        created_at: product.createdAt,
        sizes: product.sizes || [],
      });
    }
    return HttpResponse.json({ error: 'Product not found' }, { status: 404 });
  }),

  http.post('/api/products', async ({ request }) => {
    const body = await request.json() as {
      id: string;
      name: string;
      price: number;
      category_id?: string | null;
      created_at: string;
      sizes?: Array<{ id: string; name: string; price: number; sort_order: number }>;
    };
    const newProduct = {
      id: body.id || generateUUID(),
      name: body.name,
      price: body.price,
      categoryId: body.category_id,
      createdAt: body.created_at,
      sizes: (body.sizes || []).map(s => ({
        id: s.id,
        name: s.name,
        price: s.price,
        sortOrder: s.sort_order,
      })),
    };
    return HttpResponse.json(newProduct);
  }),

  http.post('/api/products/:id', async ({ params, request }) => {
    const body = await request.json() as {
      name?: string;
      price?: number;
      category_id?: string | null;
      sizes?: Array<{ id: string; name: string; price: number; sort_order: number }>;
    };
    const product = mockProducts.find(p => p.id === params.id) || mockProducts[0];
    const updatedProduct = {
      ...product,
      ...(body.name !== undefined && { name: body.name }),
      ...(body.price !== undefined && { price: body.price }),
      ...(body.category_id !== undefined && { categoryId: body.category_id }),
      ...(body.sizes !== undefined && { 
        sizes: body.sizes.map(s => ({
          id: s.id,
          name: s.name,
          price: s.price,
          sortOrder: s.sort_order,
        }))
      }),
      id: params.id as string,
    };
    return HttpResponse.json(updatedProduct);
  }),

  http.delete('/api/products/:id', () => {
    return HttpResponse.json({ success: true });
  }),

  // Categories endpoints
  http.get('/api/categories', () => {
    return HttpResponse.json({
      data: mockCategories.map(c => ({ ...c, productCount: 0 })),
      total: mockCategories.length,
    });
  }),

  http.post('/api/categories', async ({ request }) => {
    const body = await request.json() as Category;
    const newCategory: Category = { ...body, id: generateUUID() };
    return HttpResponse.json(newCategory);
  }),

  http.put('/api/categories/:id', async ({ params, request }) => {
    const body = await request.json() as Category;
    const updatedCategory: Category = { ...body, id: params.id as string };
    return HttpResponse.json(updatedCategory);
  }),

  http.delete('/api/categories/:id', () => {
    return HttpResponse.json({ success: true });
  }),

  // Orders endpoints
  http.get('/api/orders', () => {
    return HttpResponse.json({
      data: mockOrders.map(transformOrder),
      total: mockOrders.length,
    });
  }),

  http.get('/api/orders/next-number', () => {
    return HttpResponse.json({ order_number: 1003 });
  }),

  http.get('/api/orders/:id', ({ params }) => {
    const order = mockOrders.find((o) => o.id === params.id);
    if (order) {
      return HttpResponse.json(transformOrder(order));
    }
    return HttpResponse.json({ error: 'Order not found' }, { status: 404 });
  }),

  http.post('/api/orders', async ({ request }) => {
    const body = await request.json() as OrderRequestBody;
    const newOrder = snakeToCamelOrder(body);
    return HttpResponse.json(transformOrder(newOrder));
  }),

  http.delete('/api/orders/:id', () => {
    return HttpResponse.json({ success: true });
  }),

  // Debtors endpoints
  http.get('/api/debtors', () => {
    return HttpResponse.json({
      data: mockDebtors,
      total: mockDebtors.length,
    });
  }),

  http.post('/api/debtors', async ({ request }) => {
    const body = await request.json() as Debtor;
    const newDebtor: Debtor = {
      ...body,
      id: generateUUID(),
      createdAt: new Date().toISOString(),
    };
    return HttpResponse.json(newDebtor);
  }),

  http.put('/api/debtors/:id', async ({ params, request }) => {
    const body = await request.json() as Debtor;
    const updatedDebtor: Debtor = {
      ...body,
      id: params.id as string,
    };
    return HttpResponse.json(updatedDebtor);
  }),

  // Register endpoints
  http.get('/api/register', () => {
    return HttpResponse.json({
      current_balance: mockRegister.currentBalance,
      transactions: mockRegister.transactions.map((transaction) => ({
        id: transaction.id,
        type: transaction.type,
        amount: transaction.amount,
        note: transaction.note || null,
        date: transaction.date,
        order_id: transaction.orderId || null,
        user_id: transaction.userId || null,
      })),
    });
  }),

  http.get('/api/register/transactions', () => {
    return HttpResponse.json({
      data: mockTransactions.map((transaction) => ({
        id: transaction.id,
        type: transaction.type,
        amount: transaction.amount,
        note: transaction.note || null,
        date: transaction.date,
        order_id: transaction.orderId || null,
        user_id: transaction.userId || null,
      })),
      total: mockTransactions.length,
    });
  }),

  http.post('/api/register/deposit', async ({ request }) => {
    const body = await request.json() as { amount: number; note?: string | null };
    return HttpResponse.json({
      id: generateUUID(),
      type: 'deposit',
      amount: body.amount,
      note: body.note || null,
      date: new Date().toISOString(),
      order_id: null,
      user_id: null,
    });
  }),

  http.post('/api/register/withdrawal', async ({ request }) => {
    const body = await request.json() as { amount: number; note?: string | null };
    return HttpResponse.json({
      id: generateUUID(),
      type: 'withdrawal',
      amount: body.amount,
      note: body.note || null,
      date: new Date().toISOString(),
      order_id: null,
      user_id: null,
    });
  }),

  http.post('/api/register/close-shift', async ({ request }) => {
    const body = await request.json() as { note?: string | null };
    return HttpResponse.json({
      id: generateUUID(),
      type: 'shift_close',
      amount: mockRegister.currentBalance,
      note: body.note || null,
      date: new Date().toISOString(),
      order_id: null,
      user_id: null,
    });
  }),

  // Settings endpoints
  http.get('/api/settings', () => {
    return HttpResponse.json({
      id: 1,
      company_name: mockSettings.companyName,
      security: {
        password_required_for: {
          create_order: mockSettings.security.passwordRequiredFor.create_order,
          delete_order: mockSettings.security.passwordRequiredFor.delete_order,
          deposit_cash: mockSettings.security.passwordRequiredFor.deposit_cash,
          withdraw_cash: mockSettings.security.passwordRequiredFor.withdraw_cash,
          close_shift: mockSettings.security.passwordRequiredFor.close_shift,
          add_debtor: mockSettings.security.passwordRequiredFor.add_debtor,
          mark_debtor_paid: mockSettings.security.passwordRequiredFor.mark_debtor_paid,
          delete_debtor: mockSettings.security.passwordRequiredFor.delete_debtor,
          import_database: mockSettings.security.passwordRequiredFor.import_database,
        },
      },
    });
  }),

  http.post('/api/settings', async ({ request }) => {
    const body = await request.json() as { company_name?: string; security?: { password_required_for?: Record<string, boolean> } };
    const updatedCompanyName = body.company_name || mockSettings.companyName;
    const updatedSecurity = body.security?.password_required_for || mockSettings.security.passwordRequiredFor;
    return HttpResponse.json({
      id: 1,
      company_name: updatedCompanyName,
      security: {
        password_required_for: {
          create_order: updatedSecurity.create_order ?? mockSettings.security.passwordRequiredFor.create_order,
          delete_order: updatedSecurity.delete_order ?? mockSettings.security.passwordRequiredFor.delete_order,
          deposit_cash: updatedSecurity.deposit_cash ?? mockSettings.security.passwordRequiredFor.deposit_cash,
          withdraw_cash: updatedSecurity.withdraw_cash ?? mockSettings.security.passwordRequiredFor.withdraw_cash,
          close_shift: updatedSecurity.close_shift ?? mockSettings.security.passwordRequiredFor.close_shift,
          add_debtor: updatedSecurity.add_debtor ?? mockSettings.security.passwordRequiredFor.add_debtor,
          mark_debtor_paid: updatedSecurity.mark_debtor_paid ?? mockSettings.security.passwordRequiredFor.mark_debtor_paid,
          delete_debtor: updatedSecurity.delete_debtor ?? mockSettings.security.passwordRequiredFor.delete_debtor,
          import_database: updatedSecurity.import_database ?? mockSettings.security.passwordRequiredFor.import_database,
        },
      },
    });
  }),

  // Activity logs endpoints
  http.get('/api/activity', () => {
    return HttpResponse.json(mockActivityLogs);
  }),

  http.post('/api/activity', async ({ request }) => {
    const body = await request.json() as Omit<ActivityLog, 'id' | 'timestamp'>;
    const newLog: ActivityLog = {
      ...body,
      id: generateUUID(),
      timestamp: new Date().toISOString(),
    };
    return HttpResponse.json(newLog);
  }),
];

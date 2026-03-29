export const queryKeys = {
  products: {
    all: ['products'] as const,
    list: (categoryId?: string) => [...queryKeys.products.all, 'list', categoryId] as const,
    detail: (id: string) => [...queryKeys.products.all, id] as const,
  },
  categories: {
    all: ['categories'] as const,
    detail: (id: string) => [...queryKeys.categories.all, id] as const,
  },
  orders: {
    all: ['orders'] as const,
    detail: (id: string) => [...queryKeys.orders.all, id] as const,
  },
  register: {
    all: ['register'] as const,
  },
  debtors: {
    all: ['debtors'] as const,
    detail: (id: string) => [...queryKeys.debtors.all, id] as const,
  },
  settings: {
    all: ['settings'] as const,
  },
  users: {
    all: ['users'] as const,
    detail: (id: string) => [...queryKeys.users.all, id] as const,
  },
  activity: {
    all: ['activity'] as const,
  },
} as const;

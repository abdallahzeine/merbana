import { z } from "zod";

export const UUID_REGEX = /^[0-9a-f-]{36}$/;
export const TIMESTAMP_REGEX =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$/;

export const uuidSchema = z.string().regex(UUID_REGEX);
export const timestampSchema = z.string().regex(TIMESTAMP_REGEX);

export const ProductSizeResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
    price: z.number(),
    sort_order: z.number(),
  })
  .transform(({ sort_order, ...rest }) => ({
    ...rest,
    sortOrder: sort_order,
  }));

export const ProductResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
    price: z.number(),
    category_id: uuidSchema.nullable().optional(),
    created_at: timestampSchema,
    sizes: z.array(ProductSizeResponse),
    category_name: z.string().nullable().optional(),
  })
  .transform(({ category_id, created_at, ...rest }) => ({
    ...rest,
    categoryId: category_id,
    createdAt: created_at,
  }));

export const ProductListResponse = z.object({
  data: z.array(ProductResponse),
  total: z.number().nullable().optional(),
});

export const ProductCreate = z
  .object({
    id: uuidSchema,
    name: z.string(),
    price: z.number(),
    category_id: uuidSchema.nullable().optional(),
    created_at: timestampSchema,
    sizes: z.array(
      z.object({
        id: uuidSchema,
        name: z.string(),
        price: z.number(),
        sort_order: z.number().optional().default(0),
      }),
    ),
  })
  .transform(({ category_id, created_at, sizes, ...rest }) => ({
    ...rest,
    categoryId: category_id,
    createdAt: created_at,
    sizes: sizes.map(({ sort_order, ...s }) => ({
      ...s,
      sortOrder: sort_order,
    })),
  }));

export const ProductUpdate = z
  .object({
    name: z.string().optional(),
    price: z.number().optional(),
    category_id: uuidSchema.nullable().optional(),
    sizes: z
      .array(
        z.object({
          id: uuidSchema,
          name: z.string(),
          price: z.number(),
          sort_order: z.number().optional().default(0),
        }),
      )
      .optional(),
  })
  .transform(({ category_id, sizes, ...rest }) => ({
    ...rest,
    categoryId: category_id,
    sizes: sizes?.map(({ sort_order, ...s }) => ({
      ...s,
      sortOrder: sort_order,
    })),
  }));

export const CategoryResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
  })
  .transform((val) => val);

export const CategoryWithProductCountResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
    product_count: z.number(),
  })
  .transform(({ product_count, ...rest }) => ({
    ...rest,
    productCount: product_count,
  }));

export const CategoryListResponse = z.object({
  data: z.array(CategoryWithProductCountResponse),
  total: z.number().nullable().optional(),
});

export const CategoryCreate = z.object({
  id: uuidSchema,
  name: z.string(),
});

export const CategoryUpdate = z.object({
  name: z.string().optional(),
});

export const OrderItemResponse = z
  .object({
    id: uuidSchema,
    order_id: uuidSchema,
    product_id: uuidSchema.nullable().optional(),
    name: z.string(),
    price: z.number(),
    quantity: z.number(),
    size: z.string().nullable().optional(),
    subtotal: z.number(),
  })
  .transform(
    (item) => ({
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      size: item.size ?? undefined,
      subtotal: item.subtotal,
      productId: item.product_id ?? undefined,
    }),
  );

export const OrderItemCreate = z
  .object({
    product_id: uuidSchema,
    name: z.string(),
    price: z.number(),
    quantity: z.number(),
    size: z.string().nullable().optional(),
    subtotal: z.number(),
  })
  .transform(({ product_id, size, ...rest }) => ({
    ...rest,
    productId: product_id,
    size: size ?? undefined,
  }));

export const OrderResponse = z
  .object({
    id: uuidSchema,
    order_number: z.number(),
    date: timestampSchema,
    total: z.number(),
    payment_method: z.enum(["cash", "shamcash"]),
    order_type: z.enum(["dine_in", "takeaway"]),
    note: z.string().nullable().optional(),
    user_id: uuidSchema.nullable().optional(),
    user_name: z.string().nullable().optional(),
    items: z.array(OrderItemResponse),
  })
  .transform(
    ({
      order_number,
      payment_method,
      order_type,
      user_id,
      user_name,
      note,
      ...rest
    }) => ({
      ...rest,
      orderNumber: order_number,
      paymentMethod: payment_method,
      orderType: order_type,
      note: note ?? undefined,
      userId: user_id ?? undefined,
      userName: user_name ?? undefined,
    }),
  );

export const OrderSummaryResponse = z
  .object({
    id: uuidSchema,
    order_number: z.number(),
    date: timestampSchema,
    total: z.number(),
  })
  .transform(({ order_number, ...rest }) => ({
    ...rest,
    orderNumber: order_number,
  }));

export const OrderListResponse = z.object({
  data: z.array(OrderResponse),
  total: z.number().nullable().optional(),
});

export const OrderSummaryListResponse = z.object({
  data: z.array(OrderSummaryResponse),
  total: z.number().nullable().optional(),
});

export const OrderCreate = z
  .object({
    payment_method: z.enum(["cash", "shamcash"]),
    order_type: z.enum(["dine_in", "takeaway"]),
    note: z.string().nullable().optional(),
    user_id: uuidSchema.nullable().optional(),
    user_name: z.string().nullable().optional(),
    items: z.array(OrderItemCreate),
  })
  .transform(
    ({
      payment_method,
      order_type,
      user_id,
      user_name,
      note,
      ...rest
    }) => ({
      ...rest,
      paymentMethod: payment_method,
      orderType: order_type,
      note: note ?? undefined,
      userId: user_id ?? undefined,
      userName: user_name ?? undefined,
    }),
  );

export const CashTransactionResponse = z
  .object({
    id: uuidSchema,
    type: z.enum(["sale", "deposit", "withdrawal", "shift_close"]),
    amount: z.number(),
    note: z.string().nullable().optional(),
    date: timestampSchema,
    order_id: uuidSchema.nullable().optional(),
    user_id: uuidSchema.nullable().optional(),
  })
  .transform(({ order_id, user_id, ...rest }) => ({
    ...rest,
    orderId: order_id ?? undefined,
    userId: user_id ?? undefined,
  }));

export const RegisterStateResponse = z
  .object({
    current_balance: z.number(),
    transactions: z.array(CashTransactionResponse),
  })
  .transform(({ current_balance, transactions }) => ({
    currentBalance: current_balance,
    transactions,
  }));

export const DepositRequest = z.object({
  amount: z.number(),
  note: z.string().nullable().optional(),
});

export const WithdrawalRequest = z.object({
  amount: z.number(),
  note: z.string().nullable().optional(),
});

export const ShiftCloseRequest = z.object({
  note: z.string().nullable().optional(),
});

export const DebtorResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
    amount: z.number(),
    note: z.string().nullable().optional(),
    created_at: timestampSchema,
    paid_at: timestampSchema.nullable().optional(),
  })
  .transform(({ created_at, paid_at, ...rest }) => ({
    ...rest,
    createdAt: created_at,
    paidAt: paid_at,
  }));

export const DebtorListResponse = z.object({
  data: z.array(DebtorResponse),
  total: z.number().nullable().optional(),
});

export const DebtorCreate = z
  .object({
    id: uuidSchema,
    name: z.string(),
    amount: z.number(),
    note: z.string().nullable().optional(),
    created_at: timestampSchema,
  })
  .transform(({ created_at, ...rest }) => ({
    ...rest,
    createdAt: created_at,
  }));

export const MarkPaidRequest = z.object({
  paid_at: timestampSchema.nullable().optional(),
});

export const PasswordRequirementMapResponse = z
  .object({
    create_order: z.boolean(),
    delete_order: z.boolean(),
    deposit_cash: z.boolean(),
    withdraw_cash: z.boolean(),
    close_shift: z.boolean(),
    add_debtor: z.boolean(),
    mark_debtor_paid: z.boolean(),
    delete_debtor: z.boolean(),
    import_database: z.boolean(),
  })
  .transform((val) => ({
    createOrder: val.create_order,
    deleteOrder: val.delete_order,
    depositCash: val.deposit_cash,
    withdrawCash: val.withdraw_cash,
    closeShift: val.close_shift,
    addDebtor: val.add_debtor,
    markDebtorPaid: val.mark_debtor_paid,
    deleteDebtor: val.delete_debtor,
    importDatabase: val.import_database,
  }));

export const SecuritySettings = z
  .object({
    password_required_for: PasswordRequirementMapResponse,
  })
  .transform(({ password_required_for }) => ({
    passwordRequiredFor: password_required_for,
  }));

export const SettingsResponse = z
  .object({
    id: z.number(),
    company_name: z.string(),
    security: SecuritySettings,
  })
  .transform(({ company_name, ...rest }) => ({
    ...rest,
    companyName: company_name,
  }));

export const SettingsUpdate = z
  .object({
    company_name: z.string().optional(),
    security: z
      .object({
        password_required_for: z.object({
          create_order: z.boolean(),
          delete_order: z.boolean(),
          deposit_cash: z.boolean(),
          withdraw_cash: z.boolean(),
          close_shift: z.boolean(),
          add_debtor: z.boolean(),
          mark_debtor_paid: z.boolean(),
          delete_debtor: z.boolean(),
          import_database: z.boolean(),
        }),
      })
      .nullable()
      .optional(),
  })
  .transform(({ company_name, security, ...rest }) => ({
    ...rest,
    companyName: company_name,
    security: security
      ? { passwordRequiredFor: security.password_required_for }
      : undefined,
  }));

export const UserResponse = z
  .object({
    id: uuidSchema,
    name: z.string(),
    password: z.string().nullable().optional(),
    created_at: timestampSchema,
  })
  .transform(({ created_at, ...rest }) => ({
    ...rest,
    createdAt: created_at,
  }));

export const UserListResponse = z.object({
  data: z.array(UserResponse),
  total: z.number().nullable().optional(),
});

export const UserCreate = z
  .object({
    id: uuidSchema,
    name: z.string(),
    password: z.string().nullable().optional(),
    created_at: timestampSchema,
  })
  .transform(({ created_at, ...rest }) => ({
    ...rest,
    createdAt: created_at,
  }));

export const UserUpdate = z.object({
  name: z.string().optional(),
  password: z.string().nullable().optional(),
});

export const ActivityLogResponse = z
  .object({
    id: uuidSchema,
    user_id: uuidSchema.nullable().optional(),
    user_name: z.string(),
    action: z.string(),
    timestamp: timestampSchema,
  })
  .transform(({ user_id, user_name, ...rest }) => ({
    ...rest,
    userId: user_id ?? undefined,
    userName: user_name,
  }));

export const ActivityLogListResponse = z.object({
  data: z.array(ActivityLogResponse),
  total: z.number().nullable().optional(),
});

export const ErrorResponse = z.object({
  error: z.string(),
  code: z.string(),
  details: z.record(z.string(), z.unknown()).nullable().optional(),
  validation_errors: z
    .array(
      z.object({
        loc: z.array(z.string()),
        msg: z.string(),
        type: z.string(),
      }),
    )
    .nullable()
    .optional(),
});

export type ProductSize = z.infer<typeof ProductSizeResponse>;
export type Product = z.infer<typeof ProductResponse>;
export type ProductList = z.infer<typeof ProductListResponse>;
export type Category = z.infer<typeof CategoryResponse>;
export type CategoryWithProductCount = z.infer<
  typeof CategoryWithProductCountResponse
>;
export type CategoryList = z.infer<typeof CategoryListResponse>;
export type OrderItem = z.infer<typeof OrderItemResponse>;
export type Order = z.infer<typeof OrderResponse>;
export type OrderList = z.infer<typeof OrderListResponse>;
export type OrderSummary = z.infer<typeof OrderSummaryResponse>;
export type OrderSummaryList = z.infer<typeof OrderSummaryListResponse>;
export type CashTransaction = z.infer<typeof CashTransactionResponse>;
export type RegisterState = z.infer<typeof RegisterStateResponse>;
export type Debtor = z.infer<typeof DebtorResponse>;
export type DebtorList = z.infer<typeof DebtorListResponse>;
export type PasswordRequirementMap = z.infer<
  typeof PasswordRequirementMapResponse
>;
export type SecuritySettings = z.infer<typeof SecuritySettings>;
export type Settings = z.infer<typeof SettingsResponse>;
export type User = z.infer<typeof UserResponse>;
export type UserList = z.infer<typeof UserListResponse>;
export type ActivityLog = z.infer<typeof ActivityLogResponse>;
export type ActivityLogList = z.infer<typeof ActivityLogListResponse>;

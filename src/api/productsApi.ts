import { get, post, put, del } from './client';
import {
  ProductListResponse as ProductListResponseSchema,
  ProductResponse as ProductResponseSchema,
} from './schema';
import type { ProductList, Product } from './schema';

export interface ProductSizeInput {
  id: string;
  name: string;
  price: number;
  sortOrder?: number;
}

export interface ProductCreateInput {
  id: string;
  name: string;
  price: number;
  categoryId?: string | null;
  createdAt: string;
  sizes?: ProductSizeInput[];
}

export async function fetchProducts(): Promise<ProductList> {
  const raw = await get<unknown>('/products');
  return ProductListResponseSchema.parse(raw);
}

export async function fetchProduct(id: string): Promise<Product> {
  const raw = await get<unknown>(`/products/${id}`);
  return ProductResponseSchema.parse(raw);
}

export async function createProduct(data: ProductCreateInput): Promise<Product> {
  const body = {
    id: data.id,
    name: data.name,
    price: data.price,
    category_id: data.categoryId,
    created_at: data.createdAt,
    sizes: (data.sizes || []).map(s => ({
      id: s.id,
      name: s.name,
      price: s.price,
      sort_order: s.sortOrder ?? 0,
    })),
  };
  const raw = await post<unknown>('/products', body);
  return ProductResponseSchema.parse(raw);
}

export async function updateProduct(id: string, data: Partial<Product>): Promise<Product> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.price !== undefined) body.price = data.price;
  if (data.categoryId !== undefined) body.category_id = data.categoryId;
  if (data.sizes !== undefined) {
    body.sizes = data.sizes.map(s => ({
      id: s.id,
      name: s.name,
      price: s.price,
      sort_order: s.sortOrder ?? 0,
    }));
  }
  const raw = await put<unknown>(`/products/${id}`, body);
  return ProductResponseSchema.parse(raw);
}

export async function deleteProduct(id: string): Promise<void> {
  return del<void>(`/products/${id}`);
}

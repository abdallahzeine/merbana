import { get, post, del } from './client';
import {
  CategoryListResponse as CategoryListResponseSchema,
  CategoryResponse as CategoryResponseSchema,
} from './schema';
import type { CategoryList, Category } from './schema';

export async function fetchCategories(): Promise<CategoryList> {
  const raw = await get<unknown>('/categories');
  return CategoryListResponseSchema.parse(raw);
}

export async function createCategory(id: string, name: string): Promise<Category> {
  const raw = await post<unknown>('/categories', { id, name });
  return CategoryResponseSchema.parse(raw);
}

export async function deleteCategory(id: string): Promise<void> {
  return del<void>(`/categories/${id}`);
}

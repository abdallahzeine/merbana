import { get, post, put, del } from './client';
import {
  UserListResponse as UserListResponseSchema,
  UserResponse as UserResponseSchema,
} from './schema';
import type { UserList, User } from './schema';

export async function fetchUsers(): Promise<UserList> {
  const raw = await get<unknown>('/users');
  return UserListResponseSchema.parse(raw);
}

export async function createUser(data: { id: string; name: string; password?: string; createdAt: string }): Promise<User> {
  const raw = await post<unknown>('/users', {
    id: data.id,
    name: data.name,
    password: data.password ?? null,
    created_at: data.createdAt,
  });
  return UserResponseSchema.parse(raw);
}

export async function updateUser(id: string, data: { name?: string; password?: string }): Promise<User> {
  const raw = await put<unknown>(`/users/${id}`, data);
  return UserResponseSchema.parse(raw);
}

export async function deleteUser(id: string): Promise<void> {
  return del<void>(`/users/${id}`);
}


import { get, post, del } from './client';
import {
  DebtorListResponse as DebtorListResponseSchema,
  DebtorResponse as DebtorResponseSchema,
} from './schema';
import type { DebtorList, Debtor } from './schema';

export async function fetchDebtors(): Promise<DebtorList> {
  const raw = await get<unknown>('/debtors');
  return DebtorListResponseSchema.parse(raw);
}

export async function createDebtor(data: {
  id: string;
  name: string;
  amount: number;
  note?: string;
  createdAt: string;
}): Promise<Debtor> {
  const raw = await post<unknown>('/debtors', {
    id: data.id,
    name: data.name,
    amount: data.amount,
    note: data.note ?? null,
    created_at: data.createdAt,
  });
  return DebtorResponseSchema.parse(raw);
}

export async function markDebtorPaid(id: string, paidAt?: string): Promise<Debtor> {
  const raw = await post<unknown>(`/debtors/${id}/mark-paid`, {
    paid_at: paidAt ?? null,
  });
  return DebtorResponseSchema.parse(raw);
}

export async function deleteDebtor(id: string): Promise<void> {
  return del<void>(`/debtors/${id}`);
}

import { get, post } from './client';
import {
  RegisterStateResponse as RegisterStateResponseSchema,
  CashTransactionResponse as CashTransactionResponseSchema,
} from './schema';
import type { CashTransaction, RegisterState } from './schema';

export interface ShiftCloseResult {
  message: string;
  balance: number;
}

export async function fetchRegister(): Promise<RegisterState> {
  const raw = await get<unknown>('/register');
  return RegisterStateResponseSchema.parse(raw);
}

export async function depositCash(amount: number, note?: string): Promise<CashTransaction> {
  const raw = await post<unknown>('/register/deposit', { amount, note: note ?? null });
  return CashTransactionResponseSchema.parse(raw);
}

export async function withdrawCash(amount: number, note?: string): Promise<CashTransaction> {
  const raw = await post<unknown>('/register/withdrawal', { amount, note: note ?? null });
  return CashTransactionResponseSchema.parse(raw);
}

export async function closeShift(note?: string): Promise<CashTransaction | ShiftCloseResult> {
  const raw = await post<unknown>('/register/close-shift', { note: note ?? null });
  if (raw && typeof raw === 'object' && 'type' in raw) {
    return CashTransactionResponseSchema.parse(raw);
  }
  if (raw && typeof raw === 'object' && 'message' in raw && 'balance' in raw) {
    return raw as ShiftCloseResult;
  }
  throw new Error('Unexpected close shift response');
}

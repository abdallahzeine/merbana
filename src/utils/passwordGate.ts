import type { SensitiveActionKey, StoreSettings, StoreUser } from '../types/types';
import { isPasswordRequired } from './passwordPolicy';

export function shouldRequirePasswordPrompt(
  settings: StoreSettings,
  activeUser: StoreUser | null,
  actionKey: SensitiveActionKey,
): boolean {
  if (!isPasswordRequired(settings, actionKey)) return false;
  if (!activeUser?.password) return false;
  return true;
}

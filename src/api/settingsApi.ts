import { get, post } from './client';
import { SettingsResponse as SettingsResponseSchema } from './schema';
import type { Settings, PasswordRequirementMap } from './schema';

export async function fetchSettings(): Promise<Settings> {
  const raw = await get<unknown>('/settings');
  return SettingsResponseSchema.parse(raw);
}

export async function updateSettings(data: {
  companyName?: string;
  security?: { passwordRequiredFor: PasswordRequirementMap };
}): Promise<Settings> {
  const body: Record<string, unknown> = {};
  if (data.companyName !== undefined) body.company_name = data.companyName;
  if (data.security !== undefined) {
    body.security = {
      password_required_for: {
        create_order: data.security.passwordRequiredFor.createOrder,
        delete_order: data.security.passwordRequiredFor.deleteOrder,
        deposit_cash: data.security.passwordRequiredFor.depositCash,
        withdraw_cash: data.security.passwordRequiredFor.withdrawCash,
        close_shift: data.security.passwordRequiredFor.closeShift,
        add_debtor: data.security.passwordRequiredFor.addDebtor,
        mark_debtor_paid: data.security.passwordRequiredFor.markDebtorPaid,
        delete_debtor: data.security.passwordRequiredFor.deleteDebtor,
        import_database: data.security.passwordRequiredFor.importDatabase,
      },
    };
  }
  const raw = await post<unknown>('/settings', body);
  return SettingsResponseSchema.parse(raw);
}


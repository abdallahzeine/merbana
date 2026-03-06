import type { PasswordRequirementMap, SensitiveActionKey, StoreSettings } from '../types/types';

export const SENSITIVE_ACTION_LABELS: Record<SensitiveActionKey, string> = {
  create_order: 'إنشاء طلب جديد',
  delete_order: 'حذف طلب',
  deposit_cash: 'إضافة نقد للصندوق',
  withdraw_cash: 'سحب نقد من الصندوق',
  close_shift: 'إغلاق الوردية',
  add_debtor: 'إضافة دين',
  mark_debtor_paid: 'تسجيل تسديد دين',
  delete_debtor: 'حذف دين',
  import_database: 'استيراد قاعدة البيانات',
};

export const SENSITIVE_ACTIONS = Object.keys(SENSITIVE_ACTION_LABELS) as SensitiveActionKey[];

export const DEFAULT_PASSWORD_REQUIREMENTS: PasswordRequirementMap = {
  create_order: true,
  delete_order: true,
  deposit_cash: true,
  withdraw_cash: true,
  close_shift: true,
  add_debtor: true,
  mark_debtor_paid: true,
  delete_debtor: true,
  import_database: true,
};

export function isPasswordRequired(settings: StoreSettings, action: SensitiveActionKey): boolean {
  return Boolean(settings.security?.passwordRequiredFor?.[action]);
}

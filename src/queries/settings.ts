import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as settingsApi from '../api/settingsApi';
import type { PasswordRequirementMap } from '../api/schema';
import type { StoreSettings } from '../types/types';

function toStoreSettings(s: Awaited<ReturnType<typeof settingsApi.fetchSettings>>): StoreSettings {
  return {
    companyName: s.companyName,
    security: {
      passwordRequiredFor: {
        create_order: s.security.passwordRequiredFor.createOrder,
        delete_order: s.security.passwordRequiredFor.deleteOrder,
        deposit_cash: s.security.passwordRequiredFor.depositCash,
        withdraw_cash: s.security.passwordRequiredFor.withdrawCash,
        close_shift: s.security.passwordRequiredFor.closeShift,
        add_debtor: s.security.passwordRequiredFor.addDebtor,
        mark_debtor_paid: s.security.passwordRequiredFor.markDebtorPaid,
        delete_debtor: s.security.passwordRequiredFor.deleteDebtor,
        import_database: s.security.passwordRequiredFor.importDatabase,
      },
    },
  };
}

export function useSettings() {
  return useQuery({
    queryKey: queryKeys.settings.all,
    queryFn: () => settingsApi.fetchSettings(),
    select: toStoreSettings,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      companyName?: string;
      security?: { passwordRequiredFor: PasswordRequirementMap };
    }) => settingsApi.updateSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.settings.all });
    },
  });
}

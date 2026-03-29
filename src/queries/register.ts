import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as registerApi from '../api/registerApi';

export function useRegister() {
  return useQuery({
    queryKey: queryKeys.register.all,
    queryFn: () => registerApi.fetchRegister(),
  });
}

export function useDepositCash() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ amount, note }: { amount: number; note?: string }) =>
      registerApi.depositCash(amount, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

export function useWithdrawCash() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ amount, note }: { amount: number; note?: string }) =>
      registerApi.withdrawCash(amount, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

export function useCloseShift() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ note }: { note?: string }) => registerApi.closeShift(note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

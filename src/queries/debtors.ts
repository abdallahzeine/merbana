import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as debtorsApi from '../api/debtorsApi';

export function useDebtors() {
  return useQuery({
    queryKey: queryKeys.debtors.all,
    queryFn: () => debtorsApi.fetchDebtors(),
    select: (data) => data.data,
  });
}

export function useCreateDebtor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      id: string;
      name: string;
      amount: number;
      note?: string;
      createdAt: string;
    }) => debtorsApi.createDebtor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.debtors.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

export function useMarkDebtorPaid() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, paidAt }: { id: string; paidAt?: string }) =>
      debtorsApi.markDebtorPaid(id, paidAt),
    onMutate: async ({ id, paidAt }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.debtors.all });
      const previous = queryClient.getQueryData(queryKeys.debtors.all);
      queryClient.setQueryData(queryKeys.debtors.all, (old: { data: { id: string; paidAt?: string }[] } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          data: old.data.map(d => d.id === id ? { ...d, paidAt: paidAt ?? new Date().toISOString() } : d),
        };
      });
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(queryKeys.debtors.all, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.debtors.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

export function useDeleteDebtor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => debtorsApi.deleteDebtor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.debtors.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

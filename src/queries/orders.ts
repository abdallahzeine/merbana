import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as ordersApi from '../api/ordersApi';

export function useOrders(limit = 100, offset = 0) {
  return useQuery({
    queryKey: [...queryKeys.orders.all, limit, offset],
    queryFn: () => ordersApi.fetchOrders(limit, offset),
    select: (data) => data.data,
  });
}

export function useOrder(id: string) {
  return useQuery({
    queryKey: queryKeys.orders.detail(id),
    queryFn: () => ordersApi.fetchOrder(id),
    enabled: !!id,
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      items: { productId: string; name: string; price: number; quantity: number; size?: string; subtotal: number }[];
      paymentMethod: 'cash' | 'shamcash';
      orderType: 'dine_in' | 'takeaway';
      note?: string;
      userId?: string;
      userName?: string;
    }) => ordersApi.createOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.debtors.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

export function useDeleteOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ordersApi.deleteOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.register.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.debtors.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.activity.all });
    },
  });
}

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as categoriesApi from '../api/categoriesApi';

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories.all,
    queryFn: () => categoriesApi.fetchCategories(),
    select: (data) => data.data,
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) =>
      categoriesApi.createCategory(id, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.all });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => categoriesApi.deleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
    },
  });
}

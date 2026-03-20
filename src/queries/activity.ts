import { useQuery } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import * as activityApi from '../api/activityApi';

export function useActivityLog() {
  return useQuery({
    queryKey: queryKeys.activity.all,
    queryFn: () => activityApi.fetchActivityLog(),
    select: (data) => data.data,
  });
}

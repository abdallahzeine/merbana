import { get } from './client';
import type { ActivityLogList } from './schema';

export async function fetchActivityLog(): Promise<ActivityLogList> {
  return get<ActivityLogList>('/activity');
}

export async function logActivity(userId: string, userName: string, action: string): Promise<void> {
  await fetch('/api/activity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: crypto.randomUUID(),
      user_id: userId,
      user_name: userName,
      action,
      timestamp: new Date().toISOString(),
    }),
  });
}

import { vi } from 'vitest';
import { ApiError } from '../../client';
import { server } from '../../../test/mocks/server';

export const LIVE_API_BASE_URL =
  process.env.VITE_LIVE_API_BASE_URL ?? 'http://127.0.0.1:8741/api';

export const LIVE_TEST_TIMEOUT_MS = Number.parseInt(
  process.env.VITE_LIVE_TEST_TIMEOUT_MS ?? '20000',
  10,
);

export function configureLiveApiSuite(): void {
  vi.stubEnv('VITE_API_BASE_URL', LIVE_API_BASE_URL);

  // Disable MSW so requests hit the live backend directly.
  server.close();
}

export function teardownLiveApiSuite(): void {
  server.listen({ onUnhandledRequest: 'error' });
  vi.unstubAllEnvs();
}

export async function assertLiveBackendReachable(): Promise<void> {
  const response = await fetch(`${LIVE_API_BASE_URL}/users`);
  if (!response.ok) {
    throw new Error(
      `Live backend check failed: GET ${LIVE_API_BASE_URL}/users returned ${response.status}`,
    );
  }
}

function isSafeToIgnoreCleanupError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === 'NOT_FOUND';
  }

  if (error instanceof Error) {
    return /not found|404/i.test(error.message);
  }

  return false;
}

export async function safeDeleteById(
  entityName: string,
  id: string,
  remove: (id: string) => Promise<void>,
): Promise<void> {
  try {
    await remove(id);
  } catch (error) {
    if (!isSafeToIgnoreCleanupError(error)) {
      throw new Error(
        `Cleanup failed for ${entityName} '${id}': ${(error as Error).message}`,
      );
    }
  }
}

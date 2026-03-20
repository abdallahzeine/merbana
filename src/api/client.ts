import ky from 'ky';
import { ErrorResponse } from './schema';

export class ApiError extends Error {
  code: string;
  details?: Record<string, unknown>;
  validationErrors?: { loc: string[]; msg: string; type: string }[];

  constructor(message: string, code: string, details?: Record<string, unknown>, validationErrors?: { loc: string[]; msg: string; type: string }[]) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
    this.validationErrors = validationErrors;
  }
}

async function decodeError(response: Response): Promise<never> {
  let code = 'UNKNOWN_ERROR';
  let message = response.statusText || 'An error occurred';
  let details: Record<string, unknown> | undefined;
  let validationErrors: { loc: string[]; msg: string; type: string }[] | undefined;

  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    try {
      const body = await response.json();
      if (body && typeof body === 'object') {
        const parsed = ErrorResponse.safeParse(body);
        if (parsed.success) {
          message = parsed.data.error;
          code = parsed.data.code;
          details = parsed.data.details ?? undefined;
          validationErrors = parsed.data.validation_errors ?? undefined;
        }
      }
    } catch {
      // body is not JSON, use status text
    }
  }

  throw new ApiError(message, code, details, validationErrors);
}

/** Strip leading slashes so ky's prefixUrl is not bypassed. */
function normalizePath(path: string): string {
  return path.replace(/^\/+/, '');
}

const apiClient = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL ?? '/api',
  hooks: {
    beforeError: [
      async (error) => {
        if (error.response) {
          await decodeError(error.response);
        }
        return error;
      },
    ],
  },
});

export async function get<T>(path: string, searchParams?: Record<string, string | number | boolean | undefined>): Promise<T> {
  return apiClient.get(normalizePath(path), { searchParams }).json<T>();
}

export async function post<T>(path: string, json?: unknown): Promise<T> {
  return apiClient.post(normalizePath(path), { json }).json<T>();
}

export async function put<T>(path: string, json?: unknown): Promise<T> {
  return apiClient.put(normalizePath(path), { json }).json<T>();
}

export async function patch<T>(path: string, json?: unknown): Promise<T> {
  return apiClient.patch(normalizePath(path), { json }).json<T>();
}

export async function del<T>(path: string): Promise<T> {
  const response = await apiClient.delete(normalizePath(path));

  // 204 No Content (or empty bodies) should resolve as void-like responses.
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json<T>();
  }

  const raw = await response.text();
  if (!raw.trim()) {
    return undefined as T;
  }

  return JSON.parse(raw) as T;
}

export { apiClient };

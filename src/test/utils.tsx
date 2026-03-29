import { render as rtlRender, type RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import type { ReactElement, ReactNode } from 'react';
import { AuthProvider } from '../contexts/AuthContext';

interface AllTheProvidersProps {
  children: ReactNode;
}

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

function AllTheProviders({ children }: AllTheProvidersProps) {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>{children}</AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

function render(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return rtlRender(ui, { wrapper: AllTheProviders, ...options });
}

export * from '@testing-library/react';
export { render };
export { AllTheProviders, createTestQueryClient };

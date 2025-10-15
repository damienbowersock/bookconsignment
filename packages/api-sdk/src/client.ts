import { createTRPCProxyClient, httpBatchLink, loggerLink } from '@trpc/client';
import superjson from 'superjson';
import type { AppRouter } from '@bookconsign/api/trpc';

export interface ClientOptions {
  url: string;
  headers?: () => Record<string, string>;
  tenantId?: string;
}

export const createBrowserClient = ({ url, headers, tenantId }: ClientOptions) => {
  return createTRPCProxyClient<AppRouter>({
    transformer: superjson,
    links: [
      loggerLink({
        enabled: (opts) =>
          (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') ||
          opts.direction === 'down'
      }),
      httpBatchLink({
        url: `${url}/trpc`,
        headers: async () => ({
          ...(headers?.() ?? {}),
          'x-tenant-id': tenantId ?? ''
        })
      })
    ]
  });
};

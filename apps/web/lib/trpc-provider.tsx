'use client';

import type { PropsWithChildren } from 'react';
import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { getQueryClient } from './query-client';
import { trpc } from './trpc';
import { createBrowserClient } from '@bookconsign/api-sdk';
import { env } from '../env.mjs';

interface TrpcProviderProps extends PropsWithChildren {
  tenantId?: string;
  authToken?: string;
}

export const TrpcProvider = ({ tenantId, authToken, children }: TrpcProviderProps) => {
  const [queryClient] = useState(() => getQueryClient());
  const [trpcClient] = useState(() =>
    createBrowserClient({
      url: env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:4000',
      tenantId,
      headers: () => ({
        Authorization: authToken ? `Bearer ${authToken}` : ''
      })
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
};

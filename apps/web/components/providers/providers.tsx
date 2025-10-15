'use client';

import type { PropsWithChildren } from 'react';
import { useEffect, useState } from 'react';
import { ClerkProvider, useAuth } from '@clerk/nextjs';
import { ThemeProvider } from 'next-themes';
import { TrpcProvider } from '../../lib/trpc-provider';

const WithAuthToken = ({ children }: PropsWithChildren) => {
  const { getToken } = useAuth();
  const [token, setToken] = useState<string | undefined>();

  useEffect(() => {
    let mounted = true;
    void getToken({ template: 'integration_fallback' }).then((value) => {
      if (mounted) {
        setToken(value ?? undefined);
      }
    });
    return () => {
      mounted = false;
    };
  }, [getToken]);

  return <TrpcProvider authToken={token}>{children}</TrpcProvider>;
};

export const Providers = ({ children }: PropsWithChildren) => {
  return (
    <ClerkProvider>
      <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
        <WithAuthToken>{children}</WithAuthToken>
      </ThemeProvider>
    </ClerkProvider>
  );
};

'use client';

import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@bookconsign/api/trpc';

export const trpc = createTRPCReact<AppRouter>();

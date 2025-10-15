import { z } from 'zod';
import { cuidSchema } from './common';

export const tenantSchema = z.object({
  id: cuidSchema,
  name: z.string(),
  slug: z.string(),
  plan: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string()
});

export type Tenant = z.infer<typeof tenantSchema>;

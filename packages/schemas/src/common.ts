import { z } from 'zod';

export const cuidSchema = z.string().regex(/^c[^\s-]{24}$/i, 'Invalid cuid');

export const tenantIdSchema = cuidSchema;

export const isoDateSchema = z.string().datetime();

export const currencyCentsSchema = z.number().int();

export const paginationSchema = z.object({
  cursor: z.string().optional(),
  limit: z.number().int().min(1).max(100).default(20),
  search: z.string().max(255).optional()
});

export const addressSchema = z.object({
  line1: z.string(),
  line2: z.string().optional(),
  city: z.string(),
  state: z.string(),
  postalCode: z.string(),
  country: z.string().optional()
});

export const moneyValueSchema = z.object({
  currency: z.string().length(3).default('USD'),
  amountCents: currencyCentsSchema
});

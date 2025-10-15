import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const createTitleSchema = z.object({
  authorId: cuidSchema.optional(),
  isbn10: z.string().length(10).optional(),
  isbn13: z.string().length(13).optional(),
  title: z.string().min(1),
  subtitle: z.string().optional(),
  series: z.string().optional(),
  format: z.string().optional(),
  genre: z.string().optional(),
  msrpCents: z.number().int().nonnegative(),
  coverUrl: z.string().url().optional(),
  tags: z.array(z.string()).default([]),
  metadata: z.record(z.any()).optional()
});

export const updateTitleSchema = createTitleSchema.partial();

export const titleSchema = z.object({
  id: cuidSchema,
  tenantId: cuidSchema,
  authorId: cuidSchema.optional().nullable(),
  isbn10: z.string().nullable().optional(),
  isbn13: z.string().nullable().optional(),
  title: z.string(),
  subtitle: z.string().nullable().optional(),
  series: z.string().nullable().optional(),
  format: z.string().nullable().optional(),
  genre: z.string().nullable().optional(),
  msrpCents: z.number().int(),
  coverUrl: z.string().nullable().optional(),
  tags: z.array(z.string()),
  createdAt: isoDateSchema,
  updatedAt: isoDateSchema
});

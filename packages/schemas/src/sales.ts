import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const saleSourceSchema = z.enum(['SQUARE', 'CLOVER', 'LIGHTSPEED', 'MANUAL', 'IMPORT']);

export const saleImportLineSchema = z.object({
  externalId: z.string().optional(),
  occurredAt: isoDateSchema,
  titleId: cuidSchema,
  lotId: cuidSchema.optional(),
  qty: z.number().int().positive(),
  unitPriceCents: z.number().int().nonnegative(),
  discountCents: z.number().int().nonnegative().default(0),
  taxCents: z.number().int().nonnegative().default(0),
  source: saleSourceSchema.default('MANUAL'),
  locationId: cuidSchema.optional()
});

export const saleImportSchema = z.object({
  lines: z.array(saleImportLineSchema),
  idempotencyKey: z.string().uuid().optional()
});

export const saleQueryFiltersSchema = z.object({
  startDate: isoDateSchema.optional(),
  endDate: isoDateSchema.optional(),
  authorId: cuidSchema.optional(),
  titleId: cuidSchema.optional(),
  locationId: cuidSchema.optional(),
  source: saleSourceSchema.optional()
});

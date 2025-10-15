import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const inventoryIntakeLineSchema = z.object({
  titleId: cuidSchema,
  authorId: cuidSchema.optional(),
  receivedQty: z.number().int().positive(),
  costBasisCents: z.number().int().nonnegative(),
  retailPriceCents: z.number().int().nonnegative(),
  locationId: cuidSchema.optional(),
  note: z.string().optional()
});

export const inventoryIntakePayloadSchema = z.object({
  receivedAt: isoDateSchema.optional(),
  intakeReference: z.string().optional(),
  lines: z.array(inventoryIntakeLineSchema).min(1)
});

export const inventoryLotSchema = z.object({
  id: cuidSchema,
  tenantId: cuidSchema,
  titleId: cuidSchema,
  authorId: cuidSchema.optional().nullable(),
  receivedQty: z.number().int(),
  onHandQty: z.number().int(),
  reservedQty: z.number().int(),
  soldQty: z.number().int(),
  returnedQty: z.number().int(),
  damagedQty: z.number().int(),
  costBasisCents: z.number().int(),
  retailPriceCents: z.number().int(),
  receivedAt: isoDateSchema,
  locationId: cuidSchema.optional().nullable(),
  note: z.string().nullable().optional()
});

export const adjustmentReasonSchema = z.enum([
  'LOSS',
  'DAMAGE',
  'RETURN_ACCEPTED',
  'INVENTORY_CORRECTION'
]);

export const inventoryAdjustmentSchema = z.object({
  titleId: cuidSchema,
  lotId: cuidSchema.optional(),
  qtyDelta: z.number().int(),
  reason: adjustmentReasonSchema,
  note: z.string().optional()
});

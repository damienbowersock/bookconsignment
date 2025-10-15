import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const settlementStatusSchema = z.enum(['DRAFT', 'APPROVED', 'LOCKED', 'ARCHIVED']);

export const settlementGenerateSchema = z.object({
  periodStart: isoDateSchema,
  periodEnd: isoDateSchema,
  authorId: cuidSchema.optional(),
  locationId: cuidSchema.optional()
});

export const settlementApprovalSchema = z.object({
  settlementId: cuidSchema
});

export const payoutTriggerSchema = z.object({
  settlementId: cuidSchema,
  method: z.enum(['STRIPE_CONNECT', 'MANUAL']),
  metadata: z.record(z.any()).optional()
});

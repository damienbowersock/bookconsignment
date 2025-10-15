import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const authorStatusSchema = z.enum(['PENDING', 'ACTIVE', 'SUSPENDED']);

export const authorBaseSchema = z.object({
  id: cuidSchema,
  tenantId: cuidSchema,
  name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().optional(),
  taxStatus: z.string().nullable().optional(),
  taxId: z.string().nullable().optional(),
  stripeAccountId: z.string().nullable().optional(),
  status: authorStatusSchema,
  createdAt: isoDateSchema,
  updatedAt: isoDateSchema
});

export const createAuthorSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().optional(),
  taxStatus: z.string().optional(),
  taxId: z.string().optional(),
  notes: z.string().optional()
});

export const updateAuthorSchema = createAuthorSchema.partial();

export const authorLinkStatusSchema = z.enum(['PENDING', 'APPROVED', 'REJECTED', 'REVOKED']);

export const authorLinkSchema = z.object({
  id: cuidSchema,
  tenantId: cuidSchema,
  authorId: cuidSchema,
  approvedBy: cuidSchema.nullable(),
  status: authorLinkStatusSchema,
  createdAt: isoDateSchema,
  updatedAt: isoDateSchema
});

export const authorLinkRequestSchema = z.object({
  authorId: cuidSchema
});

export const authorLinkApprovalSchema = z.object({
  linkId: cuidSchema,
  approve: z.boolean(),
  note: z.string().optional()
});

export type Author = z.infer<typeof authorBaseSchema>;

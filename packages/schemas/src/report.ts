import { z } from 'zod';
import { cuidSchema, isoDateSchema } from './common';

export const reportingWindowSchema = z.object({
  startDate: isoDateSchema.optional(),
  endDate: isoDateSchema.optional(),
  locationId: cuidSchema.optional(),
  authorId: cuidSchema.optional(),
  titleId: cuidSchema.optional()
});

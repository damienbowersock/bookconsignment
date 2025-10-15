import { z } from 'zod';
import { cuidSchema } from './common';

export const roleSchema = z.enum([
  'BOOKSELLER_ADMIN',
  'STAFF',
  'AUTHOR',
  'PLATFORM_ADMIN'
]);

export const userSchema = z.object({
  id: cuidSchema,
  email: z.string().email(),
  name: z.string().optional(),
  roles: z.array(roleSchema)
});

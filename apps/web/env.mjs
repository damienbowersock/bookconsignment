import { z } from 'zod';

const runtimeSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url(),
  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: z.string().optional()
});

const serverSchema = z.object({
  CLERK_SECRET_KEY: z.string().optional(),
  CLERK_PUBLISHABLE_KEY: z.string().optional()
});

const runtimeEnv = runtimeSchema.safeParse({
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
});

if (!runtimeEnv.success) {
  console.warn('Invalid runtime environment variables', runtimeEnv.error.flatten().fieldErrors);
}

const serverEnv = serverSchema.safeParse({
  CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY,
  CLERK_PUBLISHABLE_KEY: process.env.CLERK_PUBLISHABLE_KEY
});

if (!serverEnv.success) {
  console.warn('Invalid server environment variables', serverEnv.error.flatten().fieldErrors);
}

export const env = {
  ...runtimeEnv.data,
  ...serverEnv.data
};

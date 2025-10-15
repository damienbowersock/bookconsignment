import type { UserRole } from '@prisma/client';
import type { Request, Response } from 'express';

export interface AuthenticatedUser {
  id: string;
  email: string;
  name?: string | null;
  roles: UserRole[];
  tenantIds: string[];
}

export interface AppContext {
  req: Request;
  res: Response;
  user: AuthenticatedUser | null;
  tenantId: string | null;
  requestId: string;
}

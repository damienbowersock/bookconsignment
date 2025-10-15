import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import type { Request } from 'express';
import type { AuthenticatedUser } from '../../trpc/types';
import { TenancyService } from '../tenancy/tenancy.service';

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly tenancyService: TenancyService
  ) {}

  /**
   * Temporary request authentication that reads headers injected by the reverse proxy / Clerk.
   * Replace with full Clerk/Auth.js integration during implementation.
   */
  async authenticateRequest(req: Request): Promise<{
    user: AuthenticatedUser | null;
    tenantId: string | null;
  }> {
    const userId = (req.headers['x-user-id'] as string | undefined) ?? null;
    const tenantSlug = (req.headers['x-tenant-slug'] as string | undefined) ?? null;

    if (!userId) {
      return { user: null, tenantId: await this.tenancyService.resolveTenantId(req, tenantSlug) };
    }

    const userRecord = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        tenants: true
      }
    });

    if (!userRecord) {
      this.logger.warn(`User not found for incoming request: ${userId}`);
      return { user: null, tenantId: await this.tenancyService.resolveTenantId(req, tenantSlug) };
    }

    const user: AuthenticatedUser = {
      id: userRecord.id,
      email: userRecord.email,
      name: userRecord.name,
      roles: userRecord.tenants.map((tenant) => tenant.role),
      tenantIds: userRecord.tenants.map((tenant) => tenant.tenantId)
    };

    const tenantId =
      (await this.tenancyService.resolveTenantId(req, tenantSlug)) ??
      userRecord.tenants.at(0)?.tenantId ??
      null;

    return { user, tenantId };
  }
}

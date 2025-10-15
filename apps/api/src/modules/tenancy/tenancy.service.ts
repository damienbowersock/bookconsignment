import { Injectable } from '@nestjs/common';
import type { Request } from 'express';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class TenancyService {
  constructor(private readonly prisma: PrismaService) {}

  async resolveTenantId(req: Request, slugOverride?: string | null): Promise<string | null> {
    const headerTenantId = (req.headers['x-tenant-id'] as string | undefined) ?? null;

    if (headerTenantId) {
      return headerTenantId;
    }

    const host = req.headers['x-forwarded-host'] ?? req.headers.host;
    const slugFromHost = this.extractSlugFromHost(typeof host === 'string' ? host : host?.[0]);

    const slug = slugOverride ?? slugFromHost;

    if (!slug) {
      return null;
    }

    const tenant = await this.prisma.tenant.findUnique({
      where: { slug }
    });

    return tenant?.id ?? null;
  }

  private extractSlugFromHost(host?: string): string | null {
    if (!host) {
      return null;
    }

    const [subdomain] = host.split('.');
    if (!subdomain || subdomain === 'www') {
      return null;
    }

    return subdomain.toLowerCase();
  }
}

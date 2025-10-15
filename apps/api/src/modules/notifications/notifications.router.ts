import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { TrpcService } from '../../trpc/trpc.service';
import { NotificationsService } from './notifications.service';
import { z } from 'zod';

@Injectable()
export class NotificationsRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly notifications: NotificationsService
  ) {}

  createRouter() {
    const t = this.trpc;
    const requireTenant = t.middleware(({ ctx, next }) => {
      if (!ctx.tenantId) {
        throw new TRPCError({ code: 'FORBIDDEN', message: 'Tenant context required' });
      }
      return next({ ctx: { ...ctx, tenantId: ctx.tenantId } });
    });
    const tenantProcedure = t.procedure.use(requireTenant);

    return t.router({
      test: tenantProcedure
        .input(z.object({ to: z.string().email(), template: z.string(), data: z.record(z.any()) }))
        .mutation(async ({ input }) => this.notifications.queueEmail(input))
    });
  }
}

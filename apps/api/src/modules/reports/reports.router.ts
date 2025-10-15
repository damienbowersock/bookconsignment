import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { TrpcService } from '../../trpc/trpc.service';
import { ReportsService } from './reports.service';

@Injectable()
export class ReportsRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly reports: ReportsService
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
      overview: tenantProcedure.query(async ({ ctx }) => {
        return this.reports.dashboardOverview(ctx.tenantId!);
      })
    });
  }
}

import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { TrpcService } from '../../trpc/trpc.service';
import { SalesService } from './sales.service';
import { saleImportSchema, saleQueryFiltersSchema } from '@bookconsign/schemas';

@Injectable()
export class SalesRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly salesService: SalesService
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
      list: tenantProcedure.input(saleQueryFiltersSchema.optional()).query(async ({ ctx, input }) => {
        return this.salesService.list(ctx.tenantId!, input ?? {});
      }),
      import: tenantProcedure.input(saleImportSchema).mutation(async ({ ctx, input }) => {
        return this.salesService.import(ctx.tenantId!, input);
      })
    });
  }
}

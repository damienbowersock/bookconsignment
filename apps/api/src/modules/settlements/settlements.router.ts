import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { TrpcService } from '../../trpc/trpc.service';
import {
  settlementGenerateSchema,
  settlementApprovalSchema,
  payoutTriggerSchema
} from '@bookconsign/schemas';
import { SettlementsService } from './settlements.service';

@Injectable()
export class SettlementsRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly settlements: SettlementsService
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
      generate: tenantProcedure
        .input(settlementGenerateSchema)
        .mutation(async ({ ctx, input }) => {
          return this.settlements.generate({
            tenantId: ctx.tenantId!,
            periodStart: input.periodStart,
            periodEnd: input.periodEnd,
            authorId: input.authorId
          });
        }),
      approve: tenantProcedure
        .input(settlementApprovalSchema)
        .mutation(async ({ ctx, input }) => {
          if (!ctx.user) {
            throw new TRPCError({ code: 'UNAUTHORIZED' });
          }
          return this.settlements.approve(ctx.tenantId!, input.settlementId, ctx.user.id);
        }),
      lock: tenantProcedure
        .input(settlementApprovalSchema)
        .mutation(async ({ ctx, input }) => {
          if (!ctx.user) {
            throw new TRPCError({ code: 'UNAUTHORIZED' });
          }
          return this.settlements.lock(ctx.tenantId!, input.settlementId, ctx.user.id);
        }),
      payout: tenantProcedure
        .input(payoutTriggerSchema)
        .mutation(async ({ ctx, input }) => {
          return {
            status: 'QUEUED',
            settlementId: input.settlementId,
            method: input.method
          };
        })
    });
  }
}

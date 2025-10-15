import { Injectable } from '@nestjs/common';
import { z } from 'zod';
import { TRPCError } from '@trpc/server';
import { TrpcService } from '../../trpc/trpc.service';
import { InventoryService } from './inventory.service';
import {
  inventoryIntakePayloadSchema,
  inventoryAdjustmentSchema,
  cuidSchema
} from '@bookconsign/schemas';

@Injectable()
export class InventoryRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly inventoryService: InventoryService
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
      intake: tenantProcedure
        .input(inventoryIntakePayloadSchema)
        .mutation(async ({ ctx, input }) => {
          return this.inventoryService.intake(ctx.tenantId!, {
            receivedAt: input.receivedAt ? new Date(input.receivedAt) : undefined,
            intakeReference: input.intakeReference,
            lines: input.lines
          });
        }),
      lots: tenantProcedure
        .input(
          z
            .object({
              titleId: cuidSchema.optional(),
              authorId: cuidSchema.optional()
            })
            .optional()
        )
        .query(async ({ ctx, input }) => {
          return this.inventoryService.listLots(ctx.tenantId!, input ?? {});
        }),
      adjust: tenantProcedure
        .input(inventoryAdjustmentSchema.extend({ titleId: cuidSchema }))
        .mutation(async ({ ctx, input }) => {
          return this.inventoryService.adjustStock(ctx.tenantId!, {
            ...input,
            userId: ctx.user?.id
          });
        })
    });
  }
}

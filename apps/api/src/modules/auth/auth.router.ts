import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { z } from 'zod';
import { TrpcService } from '../../trpc/trpc.service';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AuthRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly prisma: PrismaService
  ) {}

  createRouter() {
    const t = this.trpc;

    return t.router({
      me: t.procedure.query(async ({ ctx }) => {
        return ctx.user;
      }),
      tenants: t.procedure.query(async ({ ctx }) => {
        if (!ctx.user) {
          return [];
        }

        return this.prisma.userTenant.findMany({
          where: { userId: ctx.user.id },
          include: { tenant: true }
        });
      }),
      switchTenant: t.procedure
        .input(z.object({ tenantId: z.string().cuid() }))
        .mutation(async ({ ctx, input }) => {
          if (!ctx.user) {
            throw new Error('UNAUTHORIZED');
          }

          const membership = await this.prisma.userTenant.findUnique({
            where: {
              userId_tenantId: {
                userId: ctx.user.id,
                tenantId: input.tenantId
              }
            },
            include: {
              tenant: true
            }
          });

          if (!membership) {
            throw new TRPCError({ code: 'NOT_FOUND', message: 'Membership not found' });
          }

          return {
            tenant: membership.tenant
          };
        })
    });
  }
}

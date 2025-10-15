import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { z } from 'zod';
import { TrpcService } from '../../trpc/trpc.service';
import { AuthorsService } from './authors.service';
import {
  createAuthorSchema,
  authorLinkApprovalSchema,
  authorLinkRequestSchema,
  updateAuthorSchema,
  paginationSchema
} from '@bookconsign/schemas';

@Injectable()
export class AuthorsRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly authorsService: AuthorsService
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
      list: tenantProcedure
        .input(paginationSchema.extend({ search: z.string().optional() }).optional())
        .query(async ({ ctx, input }) => {
          const { items, total } = await this.authorsService.listAuthors({
            tenantId: ctx.tenantId!,
            search: input?.search,
            skip: input?.cursor ? parseInt(input.cursor, 10) : 0,
            take: input?.limit ?? 50
          });
          return { items, total };
        }),
      create: tenantProcedure
        .input(createAuthorSchema)
        .mutation(async ({ ctx, input }) => {
          return this.authorsService.createAuthor(ctx.tenantId!, {
            name: input.name,
            email: input.email,
            phone: input.phone,
            taxStatus: input.taxStatus,
            profile: input.notes ? { notes: input.notes } : undefined
          });
        }),
      update: tenantProcedure
        .input(z.object({ authorId: z.string().cuid(), data: updateAuthorSchema }))
        .mutation(async ({ ctx, input }) => {
          return this.authorsService.updateAuthor(ctx.tenantId!, input.authorId, {
            name: input.data.name,
            email: input.data.email,
            phone: input.data.phone,
            taxStatus: input.data.taxStatus,
            profile: input.data.notes ? { set: { notes: input.data.notes } } : undefined
          });
        }),
      requestLink: tenantProcedure
        .input(authorLinkRequestSchema)
        .mutation(async ({ ctx, input }) => {
          if (!ctx.user) {
            throw new TRPCError({ code: 'UNAUTHORIZED' });
          }
          return this.authorsService.requestLink(ctx.tenantId!, input.authorId, ctx.user.id);
        }),
      approveLink: tenantProcedure
        .input(authorLinkApprovalSchema)
        .mutation(async ({ ctx, input }) => {
          if (!ctx.user) {
            throw new TRPCError({ code: 'UNAUTHORIZED' });
          }
          return this.authorsService.approveLink(
            ctx.tenantId!,
            input.linkId,
            ctx.user.id,
            input.approve
          );
        })
    });
  }
}

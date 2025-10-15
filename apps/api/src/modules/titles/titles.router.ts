import { Injectable } from '@nestjs/common';
import { TRPCError } from '@trpc/server';
import { z } from 'zod';
import { TrpcService } from '../../trpc/trpc.service';
import { TitlesService } from './titles.service';
import { createTitleSchema, paginationSchema } from '@bookconsign/schemas';

@Injectable()
export class TitlesRouter {
  constructor(
    private readonly trpc: TrpcService,
    private readonly titlesService: TitlesService
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
          const { items, total } = await this.titlesService.list(ctx.tenantId!, {
            search: input?.search,
            skip: input?.cursor ? parseInt(input.cursor, 10) : 0,
            take: input?.limit ?? 50
          });
          return { items, total };
        }),
      create: tenantProcedure.input(createTitleSchema).mutation(async ({ ctx, input }) => {
        return this.titlesService.create(ctx.tenantId!, {
          title: input.title,
          subtitle: input.subtitle,
          isbn10: input.isbn10,
          isbn13: input.isbn13,
          author: input.authorId ? { connect: { id: input.authorId } } : undefined,
          tags: input.tags,
          msrpCents: input.msrpCents,
          coverUrl: input.coverUrl,
          metadata: input.metadata
        });
      })
    });
  }
}

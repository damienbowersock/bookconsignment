import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import type { Prisma } from '@prisma/client';

@Injectable()
export class TitlesService {
  constructor(private readonly prisma: PrismaService) {}

  async list(tenantId: string, params: { search?: string; take?: number; skip?: number }) {
    const where: Prisma.TitleWhereInput = {
      tenantId,
      ...(params.search
        ? {
            OR: [
              { title: { contains: params.search, mode: 'insensitive' } },
              { isbn13: { equals: params.search } },
              { isbn10: { equals: params.search } }
            ]
          }
        : undefined)
    };

    const [items, total] = await Promise.all([
      this.prisma.title.findMany({
        where,
        take: params.take ?? 50,
        skip: params.skip ?? 0,
        include: {
          author: true,
          lots: {
            select: {
              onHandQty: true,
              soldQty: true
            }
          }
        },
        orderBy: { createdAt: 'desc' }
      }),
      this.prisma.title.count({ where })
    ]);

    return {
      items: items.map((title) => ({
        ...title,
        onHandQty: title.lots.reduce((acc, lot) => acc + lot.onHandQty, 0),
        soldQty: title.lots.reduce((acc, lot) => acc + lot.soldQty, 0)
      })),
      total
    };
  }

  async create(tenantId: string, data: Prisma.TitleCreateInput) {
    return this.prisma.title.create({
      data: {
        ...data,
        tenant: {
          connect: { id: tenantId }
        }
      }
    });
  }

  async assignTerm(tenantId: string, titleId: string, termId: string, effectiveFrom: Date) {
    return this.prisma.titleTerm.create({
      data: {
        tenant: { connect: { id: tenantId } },
        title: { connect: { id: titleId } },
        term: { connect: { id: termId } },
        effectiveFrom
      }
    });
  }
}

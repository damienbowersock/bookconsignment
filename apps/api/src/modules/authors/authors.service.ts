import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import type { Prisma } from '@prisma/client';

export interface ListAuthorsParams {
  tenantId: string;
  search?: string;
  skip?: number;
  take?: number;
}

@Injectable()
export class AuthorsService {
  constructor(private readonly prisma: PrismaService) {}

  async listAuthors(params: ListAuthorsParams) {
    const { tenantId, search, skip = 0, take = 50 } = params;

    const where: Prisma.AuthorWhereInput = {
      tenantId,
      ...(search
        ? {
            OR: [
              { name: { contains: search, mode: 'insensitive' } },
              { email: { contains: search, mode: 'insensitive' } }
            ]
          }
        : undefined)
    };

    const [items, total] = await Promise.all([
      this.prisma.author.findMany({
        where,
        skip,
        take,
        orderBy: { createdAt: 'desc' },
        include: {
          links: true,
          settlements: {
            orderBy: { periodEnd: 'desc' },
            take: 1
          }
        }
      }),
      this.prisma.author.count({ where })
    ]);

    return {
      items: items.map((item) => ({
        ...item,
        linkCount: item.links.length,
        latestSettlement: item.settlements.at(0) ?? null
      })),
      total
    };
  }

  async createAuthor(tenantId: string, input: Prisma.AuthorCreateInput) {
    return this.prisma.author.create({
      data: {
        ...input,
        tenant: {
          connect: { id: tenantId }
        }
      }
    });
  }

  async updateAuthor(tenantId: string, authorId: string, input: Prisma.AuthorUpdateInput) {
    return this.prisma.author.update({
      where: {
        id: authorId,
        tenantId
      },
      data: input
    });
  }

  async requestLink(tenantId: string, authorId: string, userId: string) {
    const existing = await this.prisma.authorLink.findUnique({
      where: {
        tenantId_authorId: {
          tenantId,
          authorId
        }
      }
    });

    if (existing) {
      return existing;
    }

    return this.prisma.authorLink.create({
      data: {
        tenant: { connect: { id: tenantId } },
        author: { connect: { id: authorId } },
        status: 'PENDING',
        metadata: {
          requestedBy: userId
        }
      }
    });
  }

  async approveLink(tenantId: string, linkId: string, approverId: string, approve: boolean) {
    return this.prisma.authorLink.update({
      where: { id: linkId, tenantId },
      data: {
        status: approve ? 'APPROVED' : 'REJECTED',
        approvedBy: approve ? approverId : null
      }
    });
  }
}

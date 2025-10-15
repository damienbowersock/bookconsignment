import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { DateTime } from 'luxon';

@Injectable()
export class SettlementsService {
  constructor(private readonly prisma: PrismaService) {}

  async generate(params: {
    tenantId: string;
    periodStart: string;
    periodEnd: string;
    authorId?: string;
  }) {
    const { tenantId, authorId } = params;
    const periodStart = DateTime.fromISO(params.periodStart).toJSDate();
    const periodEnd = DateTime.fromISO(params.periodEnd).toJSDate();

    const saleLines = await this.prisma.saleLine.findMany({
      where: {
        tenantId,
        sale: {
          occurredAt: {
            gte: periodStart,
            lte: periodEnd
          }
        },
        title: {
          authorId: authorId ?? undefined
        }
      },
      include: {
        sale: true,
        title: {
          include: {
            author: true
          }
        }
      }
    });

    const grouped = new Map<string, typeof saleLines>();

    for (const line of saleLines) {
      const key = line.title.authorId ?? 'unassigned';
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key)?.push(line);
    }

    const settlements = [];

    for (const [authorKey, lines] of grouped.entries()) {
      if (authorKey === 'unassigned') {
        continue;
      }

      const author = lines[0].title.author;
      const totals = lines.reduce(
        (acc, line) => {
          acc.qtySold += line.qty;
          acc.grossCents += line.unitPriceCents * line.qty;
          acc.authorShareCents += line.authorShareCents;
          acc.storeShareCents += line.storeShareCents;
          return acc;
        },
        { qtySold: 0, grossCents: 0, authorShareCents: 0, storeShareCents: 0 }
      );

      const settlement = await this.prisma.settlement.upsert({
        where: {
          tenantId_authorId_periodStart_periodEnd: {
            tenantId,
            authorId: author?.id ?? '',
            periodStart,
            periodEnd
          }
        },
        update: {
          totalGrossCents: totals.grossCents,
          authorShareCents: totals.authorShareCents,
          storeShareCents: totals.storeShareCents
        },
        create: {
          tenantId,
          authorId: author?.id ?? '',
          periodStart,
          periodEnd,
          status: 'DRAFT',
          totalGrossCents: totals.grossCents,
          authorShareCents: totals.authorShareCents,
          storeShareCents: totals.storeShareCents
        }
      });

      await this.prisma.settlementLine.deleteMany({ where: { settlementId: settlement.id } });

      for (const line of lines) {
        await this.prisma.settlementLine.create({
          data: {
            settlementId: settlement.id,
            saleLineId: line.id,
            titleId: line.titleId,
            qtySold: line.qty,
            grossCents: line.unitPriceCents * line.qty,
            discountCents: line.sale.discountCents,
            returnCents: 0,
            feeCents: 0,
            authorShareCents: line.authorShareCents,
            storeShareCents: line.storeShareCents
          }
        });
      }

      settlements.push(settlement);
    }

    return settlements;
  }

  async approve(tenantId: string, settlementId: string, userId: string) {
    return this.prisma.settlement.update({
      where: { id: settlementId, tenantId },
      data: {
        status: 'APPROVED',
        approvedBy: userId,
        approvedAt: new Date()
      }
    });
  }

  async lock(tenantId: string, settlementId: string, userId: string) {
    return this.prisma.settlement.update({
      where: { id: settlementId, tenantId },
      data: {
        status: 'LOCKED',
        lockedAt: new Date(),
        approvedBy: userId,
        approvedAt: new Date()
      }
    });
  }
}

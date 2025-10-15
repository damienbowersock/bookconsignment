import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { DateTime } from 'luxon';

@Injectable()
export class ReportsService {
  constructor(private readonly prisma: PrismaService) {}

  async dashboardOverview(tenantId: string) {
    const now = DateTime.utc();
    const windowStart = now.minus({ days: 30 }).toJSDate();

    const [salesAgg, authorCount, liability, topTitles, pendingSettlements] = await Promise.all([
      this.prisma.saleLine.groupBy({
        by: ['titleId'],
        where: {
          tenantId,
          sale: {
            occurredAt: { gte: windowStart }
          }
        },
        _sum: {
          qty: true,
          storeShareCents: true,
          authorShareCents: true
        }
      }),
      this.prisma.author.count({
        where: { tenantId, status: 'ACTIVE' }
      }),
      this.prisma.settlement.aggregate({
        where: {
          tenantId,
          status: { in: ['APPROVED', 'LOCKED'] }
        },
        _sum: {
          authorShareCents: true
        }
      }),
      this.prisma.saleLine.findMany({
        where: {
          tenantId,
          sale: { occurredAt: { gte: windowStart } }
        },
        take: 5,
        orderBy: {
          qty: 'desc'
        },
        include: {
          title: {
            include: {
              author: true
            }
          },
          sale: true
        }
      }),
      this.prisma.settlement.findMany({
        where: {
          tenantId,
          status: 'APPROVED'
        },
        take: 5,
        orderBy: {
          periodEnd: 'asc'
        },
        include: {
          author: true
        }
      })
    ]);

    const unitsSold30d = salesAgg.reduce((acc, curr) => acc + (curr._sum.qty ?? 0), 0);
    const payoutLiabilityCents = liability._sum.authorShareCents ?? 0;

    const topTitleMapped = topTitles.map((line) => ({
      titleId: line.titleId,
      title: line.title.title,
      authorName: line.title.authorId ? line.title.author?.name ?? 'Unknown' : 'Various',
      unitsSold: line.qty
    }));

    const pendingSettlementMapped = pendingSettlements.map((settlement) => ({
      settlementId: settlement.id,
      authorName: settlement.author.name,
      periodLabel: `${DateTime.fromJSDate(settlement.periodStart).toFormat('LLL dd')} – ${DateTime.fromJSDate(settlement.periodEnd).toFormat('LLL dd')}`,
      authorShareCents: settlement.authorShareCents
    }));

    // TODO: compute real sell-through trend once cycle counts stored.
    return {
      unitsSold30d,
      unitsSoldChange: 4.2,
      sellThroughRate: 62.5,
      sellThroughChange: 1.7,
      payoutLiabilityCents,
      activeAuthors: authorCount,
      topTitles: topTitleMapped,
      pendingSettlements: pendingSettlementMapped
    };
  }
}

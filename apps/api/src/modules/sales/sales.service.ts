import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { DateTime } from 'luxon';

interface ImportSaleLine {
  externalId?: string;
  occurredAt: string;
  titleId: string;
  lotId?: string;
  qty: number;
  unitPriceCents: number;
  discountCents?: number;
  taxCents?: number;
  source: string;
  locationId?: string;
}

interface ImportPayload {
  lines: ImportSaleLine[];
  idempotencyKey?: string;
}

@Injectable()
export class SalesService {
  constructor(private readonly prisma: PrismaService) {}

  async list(tenantId: string, filters: { startDate?: string; endDate?: string }) {
    return this.prisma.sale.findMany({
      where: {
        tenantId,
        occurredAt: {
          gte: filters.startDate ? new Date(filters.startDate) : undefined,
          lte: filters.endDate ? new Date(filters.endDate) : undefined
        }
      },
      include: {
        lines: {
          include: {
            title: true,
            lot: true
          }
        }
      },
      orderBy: {
        occurredAt: 'desc'
      },
      take: 100
    });
  }

  async import(tenantId: string, payload: ImportPayload) {
    return this.prisma.$transaction(async (tx) => {
      const results = [];
      for (const line of payload.lines) {
        if (line.externalId) {
          const exists = await tx.sale.findFirst({
            where: {
              tenantId,
              source: line.source,
              externalId: line.externalId
            }
          });
          if (exists) {
            continue;
          }
        }

        const occurredAt = DateTime.fromISO(line.occurredAt).toJSDate();

        const sale = await tx.sale.create({
          data: {
            tenantId,
            occurredAt,
            source: line.source,
            externalId: line.externalId,
            subtotalCents: line.unitPriceCents * line.qty,
            discountCents: line.discountCents ?? 0,
            taxCents: line.taxCents ?? 0,
            totalCents:
              line.unitPriceCents * line.qty - (line.discountCents ?? 0) + (line.taxCents ?? 0),
            locationId: line.locationId
          }
        });

        const term = await tx.titleTerm.findFirst({
          where: {
            tenantId,
            titleId: line.titleId,
            effectiveFrom: { lte: occurredAt }
          },
          include: {
            term: true
          },
          orderBy: {
            effectiveFrom: 'desc'
          }
        });

        const authorSharePercent =
          typeof term?.term.percentSplit === 'object'
            ? (term.term.percentSplit as any).author ?? 60
            : 60;
        const storeSharePercent =
          typeof term?.term.percentSplit === 'object'
            ? (term.term.percentSplit as any).store ?? 40
            : 40;

        const gross = line.unitPriceCents * line.qty;
        const authorShareCents = Math.round((gross * authorSharePercent) / 100);
        const storeShareCents = gross - authorShareCents;

        await tx.saleLine.create({
          data: {
            tenantId,
            saleId: sale.id,
            titleId: line.titleId,
            lotId: line.lotId,
            qty: line.qty,
            unitPriceCents: line.unitPriceCents,
            appliedTermId: term?.termId,
            authorShareCents,
            storeShareCents
          }
        });

        if (line.lotId) {
          const updatedLot = await tx.inventoryLot.update({
            where: { id: line.lotId },
            data: {
              onHandQty: { decrement: line.qty },
              soldQty: { increment: line.qty }
            }
          });

          if (updatedLot.onHandQty < 0) {
            throw new Error('INSUFFICIENT_STOCK');
          }
        }

        results.push(sale);
      }

      return results;
    });
  }
}

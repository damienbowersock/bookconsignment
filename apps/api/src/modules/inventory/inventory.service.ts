import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import type { Prisma } from '@prisma/client';

export interface IntakeLine {
  titleId: string;
  authorId?: string;
  receivedQty: number;
  costBasisCents: number;
  retailPriceCents: number;
  locationId?: string;
  note?: string;
}

export interface IntakePayload {
  receivedAt?: Date;
  intakeReference?: string;
  lines: IntakeLine[];
}

@Injectable()
export class InventoryService {
  constructor(private readonly prisma: PrismaService) {}

  async intake(tenantId: string, payload: IntakePayload) {
    const receivedAt = payload.receivedAt ?? new Date();

    return this.prisma.$transaction(async (tx) => {
      const lots = await Promise.all(
        payload.lines.map((line) =>
          tx.inventoryLot.create({
            data: {
              tenantId,
              titleId: line.titleId,
              authorId: line.authorId,
              receivedQty: line.receivedQty,
              onHandQty: line.receivedQty,
              reservedQty: 0,
              soldQty: 0,
              returnedQty: 0,
              damagedQty: 0,
              costBasisCents: line.costBasisCents,
              retailPriceCents: line.retailPriceCents,
              receivedAt,
              locationId: line.locationId,
              note: line.note,
              intakeBatchId: payload.intakeReference
            }
          })
        )
      );

      return lots;
    });
  }

  async listLots(tenantId: string, params: { titleId?: string; authorId?: string }) {
    const where: Prisma.InventoryLotWhereInput = {
      tenantId,
      ...(params.titleId ? { titleId: params.titleId } : null),
      ...(params.authorId ? { authorId: params.authorId } : null)
    };

    return this.prisma.inventoryLot.findMany({
      where,
      include: {
        title: true,
        author: true,
        location: true
      },
      orderBy: {
        receivedAt: 'desc'
      }
    });
  }

  async adjustStock(
    tenantId: string,
    data: { lotId?: string; titleId: string; qtyDelta: number; reason: string; note?: string; userId?: string }
  ) {
    return this.prisma.$transaction(async (tx) => {
      const lot =
        data.lotId != null
          ? await tx.inventoryLot.findFirstOrThrow({
              where: { id: data.lotId, tenantId }
            })
          : await tx.inventoryLot.findFirstOrThrow({
              where: { tenantId, titleId: data.titleId },
              orderBy: { receivedAt: 'asc' }
            });

      const updated = await tx.inventoryLot.update({
        where: { id: lot.id },
        data: {
          onHandQty: { increment: data.qtyDelta },
          damagedQty:
            data.reason === 'DAMAGE'
              ? { increment: Math.abs(Math.min(0, data.qtyDelta)) }
              : undefined,
          returnedQty:
            data.reason === 'RETURN_ACCEPTED'
              ? { increment: Math.abs(Math.min(0, data.qtyDelta)) }
              : undefined
        }
      });

      if (updated.onHandQty < 0) {
        throw new Error('INSUFFICIENT_STOCK');
      }

      await tx.adjustment.create({
        data: {
          tenantId,
          titleId: data.titleId,
          lotId: updated.id,
          qtyDelta: data.qtyDelta,
          reason: data.reason as any,
          note: data.note,
          createdBy: data.userId
        }
      });

      return updated;
    });
  }
}

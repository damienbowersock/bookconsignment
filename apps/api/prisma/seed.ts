import { PrismaClient, UserRole } from '@prisma/client';
import { DateTime } from 'luxon';
import { SettlementsService } from '../src/modules/settlements/settlements.service';

const prisma = new PrismaClient();

async function main() {
  await prisma.$transaction([
    prisma.auditEvent.deleteMany({}),
    prisma.notification.deleteMany({}),
    prisma.payout.deleteMany({}),
    prisma.settlementLine.deleteMany({}),
    prisma.settlement.deleteMany({}),
    prisma.returnLine.deleteMany({}),
    prisma.return.deleteMany({}),
    prisma.adjustment.deleteMany({}),
    prisma.saleLine.deleteMany({}),
    prisma.sale.deleteMany({}),
    prisma.inventoryItem.deleteMany({}),
    prisma.inventoryLot.deleteMany({}),
    prisma.titleTerm.deleteMany({}),
    prisma.consignmentTerm.deleteMany({}),
    prisma.title.deleteMany({}),
    prisma.authorLink.deleteMany({}),
    prisma.author.deleteMany({}),
    prisma.userTenant.deleteMany({}),
    prisma.user.deleteMany({}),
    prisma.location.deleteMany({}),
    prisma.tenant.deleteMany({})
  ]);

  const tenant = await prisma.tenant.create({
    data: {
      name: 'Consignify Books',
      slug: 'consignify',
      plan: 'growth'
    }
  });

  const location = await prisma.location.create({
    data: {
      tenantId: tenant.id,
      name: 'Downtown Flagship',
      timezone: 'America/Los_Angeles',
      address: {
        line1: '123 Main St',
        city: 'Portland',
        state: 'OR',
        postalCode: '97204'
      }
    }
  });

  const adminUser = await prisma.user.create({
    data: {
      email: 'admin@consignify.test',
      name: 'Bailey Manager',
      authProviderId: 'clerk_admin_1'
    }
  });

  await prisma.userTenant.create({
    data: {
      userId: adminUser.id,
      tenantId: tenant.id,
      role: UserRole.BOOKSELLER_ADMIN
    }
  });

  const author = await prisma.author.create({
    data: {
      tenantId: tenant.id,
      name: 'Harper Winslow',
      email: 'harper@example.com',
      status: 'ACTIVE'
    }
  });

  await prisma.authorLink.create({
    data: {
      tenantId: tenant.id,
      authorId: author.id,
      status: 'APPROVED',
      approvedBy: adminUser.id
    }
  });

  const titleOne = await prisma.title.create({
    data: {
      tenantId: tenant.id,
      authorId: author.id,
      isbn13: '9781111111111',
      title: 'Echoes in the Stacks',
      msrpCents: 1999,
      tags: ['mystery', 'indie']
    }
  });

  const titleTwo = await prisma.title.create({
    data: {
      tenantId: tenant.id,
      authorId: author.id,
      isbn13: '9782222222222',
      title: 'Paperback Sunsets',
      msrpCents: 1699,
      tags: ['romance']
    }
  });

  const termEarly = await prisma.consignmentTerm.create({
    data: {
      tenantId: tenant.id,
      name: 'Standard 60/40',
      type: 'PERCENTAGE',
      percentSplit: { author: 60, store: 40 },
      effectiveFrom: DateTime.now().minus({ months: 2 }).toJSDate()
    }
  });

  const termLater = await prisma.consignmentTerm.create({
    data: {
      tenantId: tenant.id,
      name: 'Premium 65/35',
      type: 'PERCENTAGE',
      percentSplit: { author: 65, store: 35 },
      effectiveFrom: DateTime.now().minus({ days: 15 }).toJSDate()
    }
  });

  await prisma.titleTerm.createMany({
    data: [
      {
        tenantId: tenant.id,
        titleId: titleOne.id,
        termId: termEarly.id,
        effectiveFrom: termEarly.effectiveFrom
      },
      {
        tenantId: tenant.id,
        titleId: titleOne.id,
        termId: termLater.id,
        effectiveFrom: termLater.effectiveFrom
      },
      {
        tenantId: tenant.id,
        titleId: titleTwo.id,
        termId: termEarly.id,
        effectiveFrom: termEarly.effectiveFrom
      },
      {
        tenantId: tenant.id,
        titleId: titleTwo.id,
        termId: termLater.id,
        effectiveFrom: termLater.effectiveFrom
      }
    ]
  });

  const lotOne = await prisma.inventoryLot.create({
    data: {
      tenantId: tenant.id,
      titleId: titleOne.id,
      authorId: author.id,
      receivedQty: 10,
      onHandQty: 10,
      costBasisCents: 800,
      retailPriceCents: 1999,
      receivedAt: DateTime.now().minus({ days: 20 }).toJSDate(),
      locationId: location.id
    }
  });

  const lotTwo = await prisma.inventoryLot.create({
    data: {
      tenantId: tenant.id,
      titleId: titleTwo.id,
      authorId: author.id,
      receivedQty: 10,
      onHandQty: 10,
      costBasisCents: 700,
      retailPriceCents: 1699,
      receivedAt: DateTime.now().minus({ days: 20 }).toJSDate(),
      locationId: location.id
    }
  });

  const saleLines = [
    { titleId: titleOne.id, lotId: lotOne.id, qty: 2, unitPriceCents: 1999, occurredAt: DateTime.now().minus({ days: 18 }), term: termEarly },
    { titleId: titleOne.id, lotId: lotOne.id, qty: 1, unitPriceCents: 1999, occurredAt: DateTime.now().minus({ days: 12 }), term: termEarly },
    { titleId: titleOne.id, lotId: lotOne.id, qty: 1, unitPriceCents: 1999, occurredAt: DateTime.now().minus({ days: 5 }), term: termLater },
    { titleId: titleTwo.id, lotId: lotTwo.id, qty: 2, unitPriceCents: 1699, occurredAt: DateTime.now().minus({ days: 15 }), term: termEarly },
    { titleId: titleTwo.id, lotId: lotTwo.id, qty: 1, unitPriceCents: 1699, occurredAt: DateTime.now().minus({ days: 9 }), term: termEarly },
    { titleId: titleTwo.id, lotId: lotTwo.id, qty: 2, unitPriceCents: 1699, occurredAt: DateTime.now().minus({ days: 4 }), term: termLater },
    { titleId: titleTwo.id, lotId: lotTwo.id, qty: 1, unitPriceCents: 1699, occurredAt: DateTime.now().minus({ days: 2 }), term: termLater }
  ];

  for (const [index, line] of saleLines.entries()) {
    const sale = await prisma.sale.create({
      data: {
        tenantId: tenant.id,
        occurredAt: line.occurredAt.toJSDate(),
        source: 'MANUAL',
        externalId: `seed-${index}`,
        locationId: location.id,
        subtotalCents: line.unitPriceCents * line.qty,
        discountCents: 0,
        taxCents: 0,
        totalCents: line.unitPriceCents * line.qty
      }
    });

    const authorShare = Math.round((line.unitPriceCents * line.qty * (line.term.percentSplit as any).author) / 100);
    const storeShare = line.unitPriceCents * line.qty - authorShare;

    await prisma.saleLine.create({
      data: {
        tenantId: tenant.id,
        saleId: sale.id,
        titleId: line.titleId,
        lotId: line.lotId,
        qty: line.qty,
        unitPriceCents: line.unitPriceCents,
        appliedTermId: line.term.id,
        authorShareCents: authorShare,
        storeShareCents: storeShare
      }
    });

    await prisma.inventoryLot.update({
      where: { id: line.lotId },
      data: {
        onHandQty: { decrement: line.qty },
        soldQty: { increment: line.qty }
      }
    });
  }

  const settlementsService = new SettlementsService(prisma as any);
  await settlementsService.generate({
    tenantId: tenant.id,
    periodStart: DateTime.now().minus({ months: 1 }).startOf('month').toISO(),
    periodEnd: DateTime.now().endOf('month').toISO()
  });

  console.log('Seed data created for tenant consignify.');
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

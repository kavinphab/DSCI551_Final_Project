import { PrismaClient } from '@prisma/client';

const db = new PrismaClient();

async function main() {
  await db.generatedQuote.deleteMany();
  await db.shipment.deleteMany();
  await db.historicalQuote.deleteMany();
  await db.lane.deleteMany();
  await db.shipper.deleteMany();
  await db.carrier.deleteMany();
  await db.account.deleteMany();
  await db.user.deleteMany();

  const account = await db.account.create({
    data: {
      name: 'Echelon Logistics',
      shippers: {
        create: [
          {
            name: 'Northwood Foods',
            industry: 'Food & Beverage',
            typicalMarginTarget: 18,
            notes: 'Prefers reliable transit windows and temperature-controlled lanes.',
          },
          {
            name: 'Vector Retail',
            industry: 'Retail',
            typicalMarginTarget: 16,
            notes: 'High volume, cross-dock shipments with sensitivity to schedule.',
          },
          {
            name: 'Valence Manufacturing',
            industry: 'Manufacturing',
            typicalMarginTarget: 20,
            notes: 'Heavy equipment moves, value-conscious customer with repeat lanes.',
          },
        ],
      },
    },
  });

  const [northwood, vector, valence] = await db.shipper.findMany();

  const carriers = await Promise.all([
    db.carrier.create({ data: { name: 'Blue Ridge Freight', mode: 'Truckload' } }),
    db.carrier.create({ data: { name: 'Summit Logistics', mode: 'Truckload' } }),
    db.carrier.create({ data: { name: 'Anchor Linehaul', mode: 'FTL' } }),
  ]);

  const lanes = await Promise.all([
    db.lane.create({
      data: {
        originZip: '97201',
        destinationZip: '10001',
        originMarket: 'Portland, OR',
        destinationMarket: 'New York, NY',
        distanceMiles: 2840,
        shippers: { connect: [{ id: northwood.id }, { id: vector.id }] },
      },
    }),
    db.lane.create({
      data: {
        originZip: '60601',
        destinationZip: '75201',
        originMarket: 'Chicago, IL',
        destinationMarket: 'Dallas, TX',
        distanceMiles: 925,
        shippers: { connect: [{ id: vector.id }, { id: valence.id }] },
      },
    }),
    db.lane.create({
      data: {
        originZip: '77002',
        destinationZip: '33131',
        originMarket: 'Houston, TX',
        destinationMarket: 'Miami, FL',
        distanceMiles: 1180,
        shippers: { connect: [{ id: northwood.id }, { id: valence.id }] },
      },
    }),
    db.lane.create({
      data: {
        originZip: '94103',
        destinationZip: '90012',
        originMarket: 'San Francisco, CA',
        destinationMarket: 'Los Angeles, CA',
        distanceMiles: 383,
        shippers: { connect: [{ id: northwood.id }, { id: vector.id }, { id: valence.id }] },
      },
    }),
  ]);

  await db.historicalQuote.createMany({
    data: [
      {
        laneId: lanes[0].id,
        shipperId: northwood.id,
        carrierCost: 4500,
        sellRate: 5250,
        marginDollars: 750,
        marginPercent: 16.7,
        createdAt: new Date('2026-03-25T08:12:00Z'),
      },
      {
        laneId: lanes[0].id,
        shipperId: vector.id,
        carrierCost: 4700,
        sellRate: 5400,
        marginDollars: 700,
        marginPercent: 14.9,
        createdAt: new Date('2026-04-01T10:30:00Z'),
      },
      {
        laneId: lanes[1].id,
        shipperId: vector.id,
        carrierCost: 1350,
        sellRate: 1600,
        marginDollars: 250,
        marginPercent: 15.6,
        createdAt: new Date('2026-03-29T14:20:00Z'),
      },
      {
        laneId: lanes[1].id,
        shipperId: valence.id,
        carrierCost: 1425,
        sellRate: 1690,
        marginDollars: 265,
        marginPercent: 15.7,
        createdAt: new Date('2026-04-02T09:15:00Z'),
      },
      {
        laneId: lanes[2].id,
        shipperId: northwood.id,
        carrierCost: 2150,
        sellRate: 2550,
        marginDollars: 400,
        marginPercent: 15.7,
        createdAt: new Date('2026-03-31T13:50:00Z'),
      },
      {
        laneId: lanes[3].id,
        shipperId: valence.id,
        carrierCost: 850,
        sellRate: 990,
        marginDollars: 140,
        marginPercent: 16.5,
        createdAt: new Date('2026-04-03T11:45:00Z'),
      },
      {
        laneId: lanes[3].id,
        shipperId: vector.id,
        carrierCost: 820,
        sellRate: 960,
        marginDollars: 140,
        marginPercent: 17.1,
        createdAt: new Date('2026-04-04T07:40:00Z'),
      },
    ],
  });

  await db.user.create({
    data: {
      email: 'olivia@echelonlogistics.com',
      name: 'Olivia Chen',
      role: 'pricing analyst',
      accountId: account.id,
    },
  });

  console.log('Seed data created.');
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await db.$disconnect();
  });

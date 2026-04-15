import { prisma } from './db';
import { HistoricalQuote, Lane, Shipper } from '@prisma/client';

interface QuoteRequest {
  originZip: string;
  destinationZip: string;
  pickupDate: string;
  equipmentType: string;
  weight: number;
  shipperId: number;
}

interface QuoteResponse {
  recommendedCarrierCost: number;
  recommendedSellRate: number;
  targetMarginPercent: number;
  expectedGrossMarginDollars: number;
  expectedGrossMarginPercent: number;
  confidenceScore: number;
  rationale: {
    recentLaneRate: number;
    distanceEstimate: number;
    shipperBias: number;
    seasonalAdjustment: number;
    narrative: string[];
  };
}

const seasonalAdjustmentProfile = 1.02;

function normalize(value: number) {
  return Math.round(value * 100) / 100;
}

function computeConfidence(score: number) {
  return Math.max(45, Math.min(98, Math.round(score)));
}

async function findSimilarLane(originZip: string, destinationZip: string) {
  const exact = await prisma.lane.findFirst({
    where: { originZip, destinationZip },
  });
  if (exact) return exact;

  const byMarket = await prisma.lane.findFirst({
    where: {
      OR: [
        {
          originMarket: { contains: originZip.slice(0, 3) },
        },
        {
          destinationMarket: { contains: destinationZip.slice(0, 3) },
        },
      ],
    },
  });
  return byMarket;
}

export async function generateQuote(request: QuoteRequest): Promise<QuoteResponse> {
  const shipper = await prisma.shipper.findUnique({
    where: { id: request.shipperId },
  });
  if (!shipper) throw new Error('Shipper not found');

  const lane = await findSimilarLane(request.originZip, request.destinationZip);

  const sameLaneQuotes = lane
    ? await prisma.historicalQuote.findMany({
        where: {
          laneId: lane.id,
        },
        orderBy: { createdAt: 'desc' },
        take: 5,
      })
    : [];

  const sameShipperQuotes = await prisma.historicalQuote.findMany({
    where: { shipperId: request.shipperId }, take: 6, orderBy: { createdAt: 'desc' } });

  const recentLaneRate = sameLaneQuotes.length
    ? sameLaneQuotes.reduce((sum, row) => sum + row.carrierCost, 0) / sameLaneQuotes.length
    : 2200;

  const distanceMiles = lane?.distanceMiles ?? Math.max(300, Math.min(2800, 1 + Math.abs(parseInt(request.originZip.slice(0, 3)) - parseInt(request.destinationZip.slice(0, 3))) * 12));
  const distanceEstimate = distanceMiles * 1.95;

  const shipperBias = sameShipperQuotes.length
    ? sameShipperQuotes.reduce((sum, row) => sum + row.sellRate / row.carrierCost, 0) / sameShipperQuotes.length
    : 1.18;

  const baseCarrierCost = normalize(
    recentLaneRate * 0.5 + distanceEstimate * 0.25 + 2000 * 0.25,
  );

  const seasonalAdjustment = normalize(baseCarrierCost * (seasonalAdjustmentProfile - 1));
  const recommendedCarrierCost = normalize(baseCarrierCost * 0.98 + seasonalAdjustment * 0.02);

  const targetMarginPercent = shipper.typicalMarginTarget || 16;
  const recommendedSellRate = normalize(recommendedCarrierCost * (1 + targetMarginPercent / 100) * shipperBias * 0.99);

  const expectedGrossMarginDollars = normalize(recommendedSellRate - recommendedCarrierCost);
  const expectedGrossMarginPercent = normalize((expectedGrossMarginDollars / recommendedSellRate) * 100);

  const confidenceScore = computeConfidence(
    50 + (sameLaneQuotes.length * 8) + (sameShipperQuotes.length * 4) + (lane ? 10 : 0),
  );

  const rationale: QuoteResponse['rationale'] = {
    recentLaneRate: normalize(recentLaneRate),
    distanceEstimate: normalize(distanceEstimate),
    shipperBias: normalize(shipperBias),
    seasonalAdjustment: normalize(seasonalAdjustment),
    narrative: [
      `50% weighted toward recent similar lane quotes (${sameLaneQuotes.length} records).`,
      `25% distance-based cost estimate for ${distanceMiles} miles.`,
      `15% shipper-specific behavior using ${shipper.name}'s pricing profile.`,
      `10% placeholder seasonality / manual adjustment to capture market drift.`,
    ],
  };

  return {
    recommendedCarrierCost,
    recommendedSellRate,
    targetMarginPercent,
    expectedGrossMarginDollars,
    expectedGrossMarginPercent,
    confidenceScore,
    rationale,
  };
}

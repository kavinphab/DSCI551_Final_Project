import { prisma } from '@/lib/db';
import { generateQuote } from '@/lib/quote-engine';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const quote = await generateQuote(body);
  return NextResponse.json(quote);
}

export async function PUT(request: NextRequest) {
  const body = await request.json();
  const { quote, shipperId, originZip, destinationZip, pickupDate, equipmentType, weight } = body;

  const shipment = await prisma.shipment.create({
    data: {
      equipmentType,
      weight,
      palletCount: 0,
      pickupDate: new Date(pickupDate),
      originZip,
      destinationZip,
      shipperId,
    },
  });

  const savedQuote = await prisma.generatedQuote.create({
    data: {
      shipmentId: shipment.id,
      recommendedCarrierCost: quote.recommendedCarrierCost,
      recommendedSellRate: quote.recommendedSellRate,
      targetMarginPercent: quote.targetMarginPercent,
      confidenceScore: quote.confidenceScore,
      rationaleJson: JSON.stringify(quote.rationale),
    },
  });

  return NextResponse.json({ savedQuote, shipment });
}

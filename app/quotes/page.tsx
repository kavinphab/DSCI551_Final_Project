import { prisma } from '@/lib/db';
import Link from 'next/link';

async function getQuotes() {
  return prisma.generatedQuote.findMany({
    orderBy: { createdAt: 'desc' },
    include: { shipment: { include: { shipper: true } } },
  });
}

export default async function QuotesPage() {
  const quotes = await getQuotes();

  return (
    <main className="space-y-6 py-8">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Quote history</p>
            <h1 className="mt-3 text-3xl font-semibold text-slate-900">Saved pricing decisions</h1>
          </div>
          <Link href="/quote/new" className="inline-flex rounded-full bg-brand-500 px-5 py-3 text-sm font-semibold text-white shadow hover:bg-brand-600">
            New quote
          </Link>
        </div>

        <div className="mt-8 space-y-4">
          {quotes.map((quote) => (
            <div key={quote.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-5 hover:border-brand-300">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="text-lg font-semibold text-slate-900">{quote.shipment.originZip} → {quote.shipment.destinationZip}</p>
                  <p className="text-sm text-slate-600">{quote.shipment.equipmentType} • {quote.shipment.shipper.name}</p>
                </div>
                <div className="flex flex-col gap-1 text-right">
                  <p className="text-base font-semibold text-slate-900">{quote.recommendedSellRate.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</p>
                  <p className="text-sm text-slate-600">Margin {quote.targetMarginPercent}% • Confidence {quote.confidenceScore}%</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <Link href={`/shippers/${quote.shipment.shipperId}`} className="rounded-full bg-white px-3 py-1 text-sm text-brand-600 ring-1 ring-brand-100 transition hover:bg-brand-50">
                  {quote.shipment.shipper.name}
                </Link>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600">Saved {new Date(quote.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

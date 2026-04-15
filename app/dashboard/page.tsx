import { prisma } from '@/lib/db';
import { MetricCard } from '@/components/MetricCard';
import Link from 'next/link';

async function getDashboardData() {
  const recentQuotes = await prisma.generatedQuote.findMany({
    orderBy: { createdAt: 'desc' },
    take: 5,
    include: { shipment: { include: { shipper: true } } },
  });

  const quoteCount = await prisma.generatedQuote.count();
  const averageMargin = await prisma.generatedQuote.aggregate({
    _avg: { targetMarginPercent: true },
  });

  const topLanes = await prisma.shipment.groupBy({
    by: ['originZip', 'destinationZip'],
    _count: { id: true },
    orderBy: { _count: { id: 'desc' } },
    take: 3,
  });

  return { recentQuotes, quoteCount, averageMargin: averageMargin._avg.targetMarginPercent ?? 17, topLanes };
}

export default async function DashboardPage() {
  const data = await getDashboardData();
  return (
    <main className="space-y-8 py-8">
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard title="Quotes generated" value={`${data.quoteCount}`} description="Total saved pricing decisions in the prototype." />
        <MetricCard title="Average margin" value={`${Math.round(data.averageMargin)}%`} description="Typical recommended margin across saved quotes." />
        <MetricCard title="Top lane" value={data.topLanes[0] ? `${data.topLanes[0].originZip} → ${data.topLanes[0].destinationZip}` : 'N/A'} description="Most frequently quoted lane in the demo dataset." />
      </div>

      <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Quote history</p>
              <h2 className="mt-3 text-2xl font-semibold text-slate-900">Recent saved quotes</h2>
            </div>
            <Link href="/quotes" className="text-sm font-semibold text-brand-600 hover:text-brand-700">
              View all
            </Link>
          </div>
          <div className="mt-6 space-y-4">
            {data.recentQuotes.length ? (
              data.recentQuotes.map((quote) => (
                <div key={quote.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-semibold text-slate-900">{quote.shipment.originZip} → {quote.shipment.destinationZip}</p>
                      <p className="text-sm text-slate-600">{quote.shipment.equipmentType} for {quote.shipment.shipper.name}</p>
                    </div>
                    <p className="text-sm font-semibold text-slate-900">{quote.recommendedSellRate.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-600">No saved quotes yet. Create a new quote to populate the dashboard.</p>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
          <h2 className="text-2xl font-semibold text-slate-900">Pricing pulse</h2>
          <div className="mt-6 space-y-4">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-500">
                <span>SF → LA trend</span>
                <span>+8%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full w-8/12 rounded-full bg-brand-500" />
              </div>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-500">
                <span>Margin consistency</span>
                <span>17%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full w-7/12 rounded-full bg-emerald-500" />
              </div>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm text-slate-500">
                <span>Top customers quoted</span>
                <span>3</span>
              </div>
              <div className="grid gap-3">
                <div className="rounded-2xl bg-slate-50 p-3 text-sm text-slate-700">Northwood Foods · 15 quotes</div>
                <div className="rounded-2xl bg-slate-50 p-3 text-sm text-slate-700">Vector Retail · 12 quotes</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

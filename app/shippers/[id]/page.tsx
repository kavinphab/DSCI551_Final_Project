import { prisma } from '@/lib/db';
import { getPrismaErrorMessage } from '@/lib/prisma-safe';

interface PageProps {
  params: { id: string };
}

export const dynamic = 'force-dynamic';

async function getShipper(id: number) {
  try {
    const shipper = await prisma.shipper.findUnique({
      where: { id },
      include: { commonLanes: true, historicalQuotes: { orderBy: { createdAt: 'desc' }, take: 5 }, shipments: true },
    });

    return { shipper, error: null as string | null };
  } catch (error) {
    return { shipper: null, error: getPrismaErrorMessage(error) };
  }
}

export default async function ShipperPage({ params }: PageProps) {
  const { shipper, error } = await getShipper(Number(params.id));
  if (error) {
    return <p className="py-8 text-center text-amber-700">{error}</p>;
  }
  if (!shipper) return <p className="py-8 text-center text-slate-600">Shipper not found.</p>;

  return (
    <main className="space-y-8 py-8">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Customer profile</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">{shipper.name}</h1>
            <p className="mt-2 text-sm text-slate-600">Industry: {shipper.industry}</p>
          </div>
          <div className="rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700">Target margin {shipper.typicalMarginTarget}%</div>
        </div>
        <div className="mt-6 rounded-3xl bg-slate-50 p-6 text-sm leading-6 text-slate-700">{shipper.notes}</div>
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-xl font-semibold text-slate-900">Common lanes</h2>
          <div className="mt-4 space-y-3">
            {shipper.commonLanes.map((lane) => (
              <div key={lane.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="font-semibold text-slate-900">{lane.originZip} → {lane.destinationZip}</p>
                <p className="text-sm text-slate-600">{lane.originMarket} → {lane.destinationMarket} • {lane.distanceMiles} miles</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="text-xl font-semibold text-slate-900">Recent pricing history</h2>
          <div className="mt-4 space-y-3">
            {shipper.historicalQuotes.map((quote) => (
              <div key={quote.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">{quote.carrierCost.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })} buy / {quote.sellRate.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })} sell</p>
                <p className="text-sm text-slate-600">Margin {quote.marginPercent}% • {new Date(quote.createdAt).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

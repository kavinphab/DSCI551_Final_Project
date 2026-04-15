import Link from 'next/link';

const features = [
  { title: 'Fast quote generation', description: 'Enter a shipment in seconds and get an anchored sell price with a confidence score.' },
  { title: 'Consistent pricing', description: 'Leverages lane history, shipper behavior, and distance estimates to reduce guesswork.' },
  { title: 'Low integration burden', description: 'Works with minimal setup and seeded data for rapid onboarding.' },
  { title: 'Institutional memory', description: 'Save quotes and look back at past pricing decisions with rationale.' },
];

export default function Home() {
  return (
    <main className="space-y-12 py-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-10 shadow-soft">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Echelon MVP</p>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
              Quote faster. Price smarter. Keep your team aligned.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Echelon helps small and mid-market 3PL pricing teams generate reliable truckload quotes without deep TMS integration. Demo the workflow from shipment entry to recommended quote and saved history.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/quote/new" className="inline-flex rounded-full bg-brand-500 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-brand-600">
                Create quote
              </Link>
              <Link href="/dashboard" className="inline-flex rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 hover:border-brand-500 hover:text-brand-700">
                View dashboard
              </Link>
            </div>
          </div>
          <div className="rounded-3xl bg-slate-50 p-8 shadow-soft">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Demo metrics</p>
            <div className="mt-8 space-y-5">
              <div className="rounded-3xl bg-white p-5 shadow-sm">
                <p className="text-3xl font-semibold text-slate-900">42</p>
                <p className="mt-2 text-sm text-slate-600">Quotes generated this week</p>
              </div>
              <div className="rounded-3xl bg-white p-5 shadow-sm">
                <p className="text-3xl font-semibold text-slate-900">17.3%</p>
                <p className="mt-2 text-sm text-slate-600">Average margin across saved quotes</p>
              </div>
              <div className="rounded-3xl bg-white p-5 shadow-sm">
                <p className="text-3xl font-semibold text-slate-900">SF → LA</p>
                <p className="mt-2 text-sm text-slate-600">Top quoted lane in demo data</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        {features.map((feature) => (
          <div key={feature.title} className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
            <h2 className="text-xl font-semibold text-slate-900">{feature.title}</h2>
            <p className="mt-4 text-slate-600">{feature.description}</p>
          </div>
        ))}
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <h2 className="text-2xl font-semibold text-slate-900">Demo flow</h2>
        <ol className="mt-6 space-y-4 text-slate-600">
          <li>1. Click “Create Quote” and enter a shipment with origin, destination, weight, and shipper.</li>
          <li>2. Generate a quote that shows recommended buy/sell pricing, target margin, and confidence.</li>
          <li>3. Save the quote and review the saved quote history.</li>
          <li>4. Open any quote to inspect the full pricing rationale and data drivers.</li>
        </ol>
      </section>
    </main>
  );
}

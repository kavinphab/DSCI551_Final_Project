export default function SettingsPage() {
  return (
    <main className="space-y-8 py-8">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <h1 className="text-3xl font-semibold text-slate-900">Admin & settings</h1>
        <p className="mt-3 text-slate-600">Simple configuration for the demo prototype. This page gives a sense of where account-level controls would live.</p>

        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-xl font-semibold text-slate-900">Account</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">Echelon Logistics, a demo 3PL account with seeded shippers and pricing history.</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-xl font-semibold text-slate-900">Quote engine</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">Rules-based pricing uses lane history, distance estimation, shipper behavior, and market adjustment weights.</p>
          </div>
        </div>
      </div>
    </main>
  );
}

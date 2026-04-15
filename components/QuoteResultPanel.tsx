function confidenceLabel(score: number) {
  if (score >= 80) return { label: 'High', color: 'bg-emerald-100 text-emerald-800' };
  if (score >= 60) return { label: 'Medium', color: 'bg-amber-100 text-amber-800' };
  return { label: 'Low', color: 'bg-rose-100 text-rose-800' };
}

export function QuoteResultPanel({ data }: { data: any }) {
  const badge = confidenceLabel(data.confidenceScore);

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-slate-500">Recommended quote</p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-900">{data.recommendedSellRate.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</h2>
        </div>
        <span className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${badge.color}`}>{badge.label} confidence</span>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-3xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Carrier cost</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{data.recommendedCarrierCost.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</p>
        </div>
        <div className="rounded-3xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Target margin</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{data.targetMarginPercent}%</p>
        </div>
        <div className="rounded-3xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Margin dollars</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{data.expectedGrossMarginDollars.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</p>
        </div>
      </div>

      <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4">
        <p className="text-sm font-semibold text-slate-700">Why this quote?</p>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
          {data.rationale.narrative.map((item: string) => (
            <li key={item} className="flex gap-3">
              <span className="mt-1 inline-flex h-2 w-2 rounded-full bg-brand-500" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

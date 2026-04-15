'use client';

import { useMemo, useState } from 'react';
import { QuoteResultPanel } from '@/components/QuoteResultPanel';

interface QuoteFormProps {
  shippers: Array<{ id: number; name: string }>;
}

export function QuoteForm({ shippers }: QuoteFormProps) {
  const [form, setForm] = useState({
    shipperId: shippers[0]?.id ?? 1,
    originZip: '94103',
    destinationZip: '90012',
    pickupDate: new Date().toISOString().slice(0, 10),
    equipmentType: 'Dry van',
    weight: 28700,
  });
  const [result, setResult] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState('');

  const shipperOptions = useMemo(
    () => shippers.map((shipper) => ({ value: shipper.id, label: shipper.name })),
    [shippers],
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setStatus('Generating quote...');
    const response = await fetch('/api/quote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    const data = await response.json();
    setResult(data);
    setStatus('Quote generated. Save when ready.');
  };

  const handleSave = async () => {
    if (!result) return;
    setSaving(true);
    await fetch('/api/quote', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, quote: result }),
    });
    setSaving(false);
    setStatus('Quote saved to history.');
  };

  return (
    <main className="space-y-8 py-8">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Create quote</p>
            <h1 className="mt-3 text-3xl font-semibold text-slate-900">Enter shipment details</h1>
          </div>
          <p className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-600">Designed for low-integration quoting</p>
        </div>
        <form className="mt-8 grid gap-6 lg:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Shipper</span>
            <select
              value={form.shipperId}
              onChange={(event) => setForm({ ...form, shipperId: Number(event.target.value) })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            >
              {shipperOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Equipment type</span>
            <select
              value={form.equipmentType}
              onChange={(event) => setForm({ ...form, equipmentType: event.target.value })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            >
              <option>Dry van</option>
              <option>Reefer</option>
              <option>Flatbed</option>
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Origin ZIP</span>
            <input
              value={form.originZip}
              onChange={(event) => setForm({ ...form, originZip: event.target.value })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Destination ZIP</span>
            <input
              value={form.destinationZip}
              onChange={(event) => setForm({ ...form, destinationZip: event.target.value })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Pickup date</span>
            <input
              type="date"
              value={form.pickupDate}
              onChange={(event) => setForm({ ...form, pickupDate: event.target.value })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Weight (lbs)</span>
            <input
              type="number"
              value={form.weight}
              onChange={(event) => setForm({ ...form, weight: Number(event.target.value) })}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm outline-none focus:border-brand-500"
            />
          </label>

          <div className="lg:col-span-2 flex flex-col gap-4 sm:flex-row sm:items-center">
            <button type="submit" className="inline-flex grow items-center justify-center rounded-2xl bg-brand-500 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-brand-600">
              Generate quote
            </button>
            <button type="button" onClick={handleSave} disabled={!result || saving} className="inline-flex grow items-center justify-center rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm hover:border-brand-500 hover:text-brand-700 disabled:cursor-not-allowed disabled:opacity-60">
              {saving ? 'Saving...' : 'Save quote'}
            </button>
          </div>
        </form>
        {status && <p className="mt-4 text-sm text-slate-600">{status}</p>}
      </div>

      {result && <QuoteResultPanel data={result} />}
    </main>
  );
}

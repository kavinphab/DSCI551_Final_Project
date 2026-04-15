import Link from 'next/link';

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-120px)] max-w-xl items-center justify-center py-12">
      <div className="w-full rounded-3xl border border-slate-200 bg-white p-10 shadow-soft">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Mock login</p>
        <h1 className="mt-4 text-3xl font-semibold text-slate-900">Welcome back, pricing analyst</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">No account setup needed — this demo uses seeded credentials and a realistic workflow.</p>
        <div className="mt-8 space-y-4">
          <button className="w-full rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white shadow hover:bg-brand-600">Continue as Olivia Chen</button>
          <button className="w-full rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:border-brand-500 hover:text-brand-700">
            View as guest
          </button>
        </div>
        <p className="mt-6 text-sm text-slate-500">Need a quick demo? Go to the <Link href="/dashboard" className="font-semibold text-brand-600 underline">dashboard</Link>.</p>
      </div>
    </main>
  );
}

import { prisma } from '@/lib/db';
import { getPrismaErrorMessage } from '@/lib/prisma-safe';
import { QuoteForm } from '@/components/QuoteForm';

export const dynamic = 'force-dynamic';

async function getShippers() {
  try {
    const shippers = await prisma.shipper.findMany();
    return { shippers, error: null as string | null };
  } catch (error) {
    return { shippers: [], error: getPrismaErrorMessage(error) };
  }
}

export default async function CreateQuotePage() {
  const { shippers, error } = await getShippers();

  if (error) {
    return (
      <main className="space-y-8 py-8">
        <div className="rounded-3xl border border-amber-200 bg-amber-50 p-8 text-amber-900 shadow-soft">
          <p className="text-sm uppercase tracking-[0.24em] text-amber-700">Database unavailable</p>
          <h1 className="mt-3 text-3xl font-semibold">Create quote</h1>
          <p className="mt-4 text-sm">{error}</p>
        </div>
      </main>
    );
  }

  return <QuoteForm shippers={shippers} />;
}

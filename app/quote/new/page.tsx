import { prisma } from '@/lib/db';
import { QuoteForm } from '@/components/QuoteForm';

async function getShippers() {
  return prisma.shipper.findMany();
}

export default async function CreateQuotePage() {
  const shippers = await getShippers();
  return <QuoteForm shippers={shippers} />;
}

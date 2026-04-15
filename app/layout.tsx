import type { Metadata } from 'next';
import './globals.css';
import { TopNav } from '@/components/TopNav';

export const metadata: Metadata = {
  title: 'Echelon Pricing',
  description: 'Low-integration pricing automation for 3PLs and freight brokers.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <TopNav />
          {children}
        </div>
      </body>
    </html>
  );
}

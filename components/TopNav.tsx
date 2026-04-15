import Link from 'next/link';

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/quote/new', label: 'Create Quote' },
  { href: '/quotes', label: 'History' },
  { href: '/settings', label: 'Settings' },
];

export function TopNav() {
  return (
    <header className="mb-6 flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-soft backdrop-blur-xl md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Echelon</p>
        <h1 className="text-2xl font-semibold text-slate-900">Pricing automation for 3PL pricing teams</h1>
      </div>
      <nav className="flex flex-wrap gap-3">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-500 hover:text-brand-700"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}

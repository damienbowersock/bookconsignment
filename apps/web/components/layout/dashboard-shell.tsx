'use client';

import type { PropsWithChildren } from 'react';
import { usePathname } from 'next/navigation';
import { AppShell } from '@bookconsign/ui';
import { UserButton } from '@clerk/nextjs';
import { Button } from '@bookconsign/ui';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/authors', label: 'Authors' },
  { href: '/inventory', label: 'Inventory' },
  { href: '/sales', label: 'Sales' },
  { href: '/returns', label: 'Returns' },
  { href: '/settlements', label: 'Settlements' },
  { href: '/reports', label: 'Reports' },
  { href: '/settings', label: 'Settings' }
];

export const DashboardShell = ({ children }: PropsWithChildren) => {
  const pathname = usePathname();

  return (
    <AppShell
      navItems={navItems.map((item) => ({
        ...item,
        current: pathname === item.href
      }))}
      topBar={
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">Bookstore HQ</h1>
            <p className="text-sm text-slate-400">Multi-location consignment performance overview</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" size="sm">
              New Intake
            </Button>
            <Button size="sm">Generate Settlement</Button>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      }
    >
      {children}
    </AppShell>
  );
};

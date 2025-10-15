import type { PropsWithChildren, ReactNode } from 'react';
import { clsx } from 'clsx';

export interface NavItem {
  href: string;
  label: string;
  icon?: ReactNode;
  current?: boolean;
}

export interface AppShellProps extends PropsWithChildren {
  navItems: NavItem[];
  topBar?: ReactNode;
  footer?: ReactNode;
}

export const AppShell = ({ navItems, topBar, footer, children }: AppShellProps) => {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-50">
      <aside className="hidden w-72 shrink-0 border-r border-slate-800 bg-slate-900/60 backdrop-blur lg:block">
        <div className="p-6">
          <div className="text-2xl font-semibold tracking-tight">Consignify</div>
        </div>
        <nav className="space-y-1 px-4">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition hover:bg-slate-800/60 hover:text-white',
                item.current ? 'bg-slate-800 text-white' : 'text-slate-300'
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
      </aside>
      <div className="flex w-full flex-1 flex-col">
        <header className="border-b border-slate-800 bg-slate-900/40 px-6 py-4">{topBar}</header>
        <main className="flex-1 bg-slate-950/60 px-6 py-6">{children}</main>
        {footer ? (
          <footer className="border-t border-slate-800 bg-slate-900/40 px-6 py-4 text-sm text-slate-400">
            {footer}
          </footer>
        ) : null}
      </div>
    </div>
  );
};

import { Suspense } from 'react';
import { AuthorPortal } from '../../components/portal/author-portal';

export default function PortalPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Author Portal</h2>
        <p className="text-sm text-slate-400">
          Review stocking levels, sales velocity, issued statements, and payout statuses across your
          linked bookstores.
        </p>
      </header>
      <Suspense fallback={<div className="text-slate-400">Loading portal data…</div>}>
        <AuthorPortal />
      </Suspense>
    </div>
  );
}

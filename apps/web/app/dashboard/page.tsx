import { Suspense } from 'react';
import { DashboardOverview } from '../../components/dashboard/overview';

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="text-slate-400">Loading dashboard…</div>}>
      <DashboardOverview />
    </Suspense>
  );
}

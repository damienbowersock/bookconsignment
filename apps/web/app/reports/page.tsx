export default function ReportsPage() {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold text-white">Analytics & Reporting</h2>
        <p className="text-sm text-slate-400">
          Explore sell-through, aging, velocity, and liability reports with CSV/PDF export options.
        </p>
      </header>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        Reporting data sources are available via tRPC. This page will host interactive tables and
        charts powered by React Query and the shared UI kit.
      </div>
    </div>
  );
}

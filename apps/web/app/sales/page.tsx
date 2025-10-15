export default function SalesPage() {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold text-white">Sales Ingestion</h2>
        <p className="text-sm text-slate-400">
          Import POS data, reconcile manual entries, and monitor webhook delivery for connected
          providers.
        </p>
      </header>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        CSV import previews and webhook feed UI will live here. Use the API to test Square adapter
        payload normalization.
      </div>
    </div>
  );
}

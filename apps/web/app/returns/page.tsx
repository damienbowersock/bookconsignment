export default function ReturnsPage() {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold text-white">Returns & Recall</h2>
        <p className="text-sm text-slate-400">
          Initiate consignment returns, track transit statuses, and generate packing slips for
          authors.
        </p>
      </header>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        Workflow components will surface soon. For now, Returns API endpoints support status
        transitions and author notifications.
      </div>
    </div>
  );
}

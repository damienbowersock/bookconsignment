export default function InventoryPage() {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold text-white">Inventory</h2>
        <p className="text-sm text-slate-400">
          Track on-hand, reserved, and aging stock. Intake new lots, print labels, and reconcile
          cycle counts.
        </p>
      </header>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        Inventory dashboards and lot tables coming soon. The API already supports batch intake and
        adjustments via tRPC.
      </div>
    </div>
  );
}

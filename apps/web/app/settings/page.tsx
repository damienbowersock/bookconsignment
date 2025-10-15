export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <header>
        <h2 className="text-2xl font-semibold text-white">Settings</h2>
        <p className="text-sm text-slate-400">
          Manage branding, tax policies, default terms, feature flags, and integrations.
        </p>
      </header>
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        Configuration forms will land here. Environment variables are validated via zod in
        `apps/web/env.mjs`.
      </div>
    </div>
  );
}

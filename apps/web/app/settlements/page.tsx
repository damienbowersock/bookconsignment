import { SettlementGenerator } from '../../components/settlements/settlement-generator';

export default function SettlementsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Settlements & Payouts</h2>
        <p className="text-sm text-slate-400">
          Close periods, review author statements, approve payouts, and sync with Stripe Connect.
        </p>
      </header>
      <SettlementGenerator />
    </div>
  );
}

import type { ReactNode } from 'react';
import { formatMoney } from '@bookconsign/lib';

export interface KpiProps {
  label: string;
  value: number | string;
  change?: number;
  icon?: ReactNode;
  currency?: boolean;
}

export const Kpi = ({ label, value, change, icon, currency }: KpiProps) => {
  const displayValue =
    typeof value === 'number' && currency ? formatMoney(value) : value.toLocaleString?.() ?? value;

  return (
    <div className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="flex items-center justify-between text-sm text-slate-400">
        {label}
        {icon}
      </div>
      <div className="mt-4 text-3xl font-semibold text-white">{displayValue}</div>
      {typeof change === 'number' ? (
        <div
          className={
            change >= 0 ? 'mt-2 text-sm text-emerald-400' : 'mt-2 text-sm text-rose-400'
          }
        >
          {change > 0 ? '+' : ''}
          {change.toFixed(1)}%
        </div>
      ) : null}
    </div>
  );
};

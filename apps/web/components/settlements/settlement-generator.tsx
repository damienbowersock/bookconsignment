'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { trpc } from '../../lib/trpc';
import { Button, Card } from '@bookconsign/ui';

interface FormValues {
  periodStart: string;
  periodEnd: string;
}

export const SettlementGenerator = () => {
  const form = useForm<FormValues>({
    defaultValues: {
      periodStart: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
        .toISOString()
        .slice(0, 10),
      periodEnd: new Date().toISOString().slice(0, 10)
    }
  });
  const [message, setMessage] = useState<string | null>(null);
  const utils = trpc.useUtils();
  const mutation = trpc.settlements.generate.useMutation({
    onSuccess: async (data) => {
      setMessage(`Generated ${data.length} settlement(s)`);
      await utils.reports.overview.invalidate();
    },
    onError: (error) => {
      setMessage(error.message);
    }
  });

  const onSubmit = form.handleSubmit((values) => {
    mutation.mutate({
      periodStart: new Date(values.periodStart).toISOString(),
      periodEnd: new Date(values.periodEnd).toISOString()
    });
  });

  return (
    <Card
      title="Generate settlements"
      description="Build statements for the selected period and enqueue payouts after review."
      actions={
        <Button size="sm" onClick={onSubmit} loading={mutation.isLoading}>
          Run generation
        </Button>
      }
    >
      <form className="flex flex-col gap-4 text-sm text-slate-200" onSubmit={onSubmit}>
        <label className="flex flex-col gap-1">
          Period start
          <input
            type="date"
            className="rounded-md border border-slate-700 bg-slate-900/60 px-3 py-2"
            {...form.register('periodStart', { required: true })}
          />
        </label>
        <label className="flex flex-col gap-1">
          Period end
          <input
            type="date"
            className="rounded-md border border-slate-700 bg-slate-900/60 px-3 py-2"
            {...form.register('periodEnd', { required: true })}
          />
        </label>
        {message ? <p className="text-xs text-emerald-400">{message}</p> : null}
      </form>
    </Card>
  );
};

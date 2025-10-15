'use client';

import { useMemo } from 'react';
import { trpc } from '../../lib/trpc';
import { Kpi, Card, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell } from '@bookconsign/ui';

export const DashboardOverview = () => {
  const { data, isLoading } = trpc.reports.overview.useQuery(undefined, {
    staleTime: 60_000
  });

  const kpis = useMemo(
    () => [
      {
        label: 'Units Sold (30d)',
        value: data?.unitsSold30d ?? 0,
        change: data?.unitsSoldChange
      },
      {
        label: 'Sell-Through %',
        value: (data?.sellThroughRate ?? 0).toFixed(1),
        change: data?.sellThroughChange
      },
      {
        label: 'Payout Liability',
        value: data?.payoutLiabilityCents ?? 0,
        currency: true
      },
      {
        label: 'Active Authors',
        value: data?.activeAuthors ?? 0
      }
    ],
    [data]
  );

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <Kpi key={kpi.label} {...kpi} />
        ))}
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Top Titles" description="Sell-through performance last 30 days">
          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Title</TableHeaderCell>
                <TableHeaderCell>Author</TableHeaderCell>
                <TableHeaderCell className="text-right">Units Sold</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data?.topTitles ?? []).map((title) => (
                <TableRow key={title.titleId}>
                  <TableCell>{title.title}</TableCell>
                  <TableCell>{title.authorName}</TableCell>
                  <TableCell className="text-right">{title.unitsSold}</TableCell>
                </TableRow>
              ))}
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-slate-400">
                    Loading dashboard metrics…
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Card>

        <Card title="Upcoming Settlements" description="Statements awaiting approval">
          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Author</TableHeaderCell>
                <TableHeaderCell>Period</TableHeaderCell>
                <TableHeaderCell className="text-right">Author Share</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data?.pendingSettlements ?? []).map((settlement) => (
                <TableRow key={settlement.settlementId}>
                  <TableCell>{settlement.authorName}</TableCell>
                  <TableCell>{settlement.periodLabel}</TableCell>
                  <TableCell className="text-right">
                    ${(settlement.authorShareCents / 100).toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-slate-400">
                    Loading settlement pipeline…
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
};

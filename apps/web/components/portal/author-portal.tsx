'use client';

import { trpc } from '../../lib/trpc';
import { Card, Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from '@bookconsign/ui';

export const AuthorPortal = () => {
  const { data } = trpc.authors.list.useQuery({ limit: 10 });
  const overview = trpc.reports.overview.useQuery();

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card title="Linked bookstores" description="Authors can request additional links.">
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Store</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(data?.items ?? []).map((author) => (
              <TableRow key={author.id}>
                <TableCell>{author.name}</TableCell>
                <TableCell>{author.status}</TableCell>
              </TableRow>
            ))}
            {(data?.items?.length ?? 0) === 0 && (
              <TableRow>
                <TableCell colSpan={2} className="py-6 text-center text-slate-400">
                  No author records yet. Seed data creates one active link for demo.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
      <Card title="Statements" description="Latest settlement activity" className="space-y-2">
        <div className="text-sm text-slate-300">
          Payout liability:{' '}
          <span className="font-semibold text-emerald-400">
            ${((overview.data?.payoutLiabilityCents ?? 0) / 100).toFixed(2)}
          </span>
        </div>
        <div className="text-xs text-slate-400">
          Author portal wiring is ready for Clerk role-based routing. Use the settlements router to
          pull issued statements and render PDF downloads.
        </div>
      </Card>
    </div>
  );
};

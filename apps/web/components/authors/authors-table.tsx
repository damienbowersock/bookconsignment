'use client';

import { useMemo } from 'react';
import { trpc } from '../../lib/trpc';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Button
} from '@bookconsign/ui';

export const AuthorsTable = () => {
  const { data, isLoading } = trpc.authors.list.useQuery({ limit: 50 });

  const rows = useMemo(() => data?.items ?? [], [data]);

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeaderCell>Name</TableHeaderCell>
          <TableHeaderCell>Email</TableHeaderCell>
          <TableHeaderCell>Status</TableHeaderCell>
          <TableHeaderCell>Linked Stores</TableHeaderCell>
          <TableHeaderCell className="text-right">Actions</TableHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((author) => (
          <TableRow key={author.id}>
            <TableCell>{author.name}</TableCell>
            <TableCell className="text-slate-400">{author.email}</TableCell>
            <TableCell>
              <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs font-medium text-emerald-400">
                {author.status}
              </span>
            </TableCell>
            <TableCell>{author.linkCount}</TableCell>
            <TableCell className="flex justify-end gap-2">
              <Button size="sm" variant="ghost">
                View
              </Button>
              <Button size="sm" variant="secondary">
                Statement
              </Button>
            </TableCell>
        ))}
        {isLoading ? (
          <TableRow>
            <TableCell colSpan={5} className="py-10 text-center text-slate-400">
              Fetching author records…
            </TableCell>
          </TableRow>
        ) : null}
      </TableBody>
    </Table>
  );
};

import type { PropsWithChildren, ReactNode } from 'react';
import { clsx } from 'clsx';

export interface TableProps extends PropsWithChildren {
  footer?: ReactNode;
  className?: string;
}

export const Table = ({ children, footer, className }: TableProps) => (
  <div className={clsx('overflow-hidden rounded-xl border border-slate-800', className)}>
    <table className="min-w-full divide-y divide-slate-800">{children}</table>
    {footer ? <div className="border-t border-slate-800 bg-slate-900/60 p-4">{footer}</div> : null}
  </div>
);

export const TableHead = ({ children }: PropsWithChildren) => (
  <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
    {children}
  </thead>
);

export const TableBody = ({ children }: PropsWithChildren) => (
  <tbody className="divide-y divide-slate-800 bg-slate-900/20 text-sm text-slate-200">{children}</tbody>
);

export const TableRow = ({ children }: PropsWithChildren) => <tr>{children}</tr>;

export const TableCell = ({
  children,
  className
}: PropsWithChildren<{ className?: string }>) => (
  <td className={clsx('px-4 py-3 align-middle', className)}>{children}</td>
);

export const TableHeaderCell = ({
  children,
  className
}: PropsWithChildren<{ className?: string }>) => (
  <th scope="col" className={clsx('px-4 py-3 text-left font-medium', className)}>
    {children}
  </th>
);

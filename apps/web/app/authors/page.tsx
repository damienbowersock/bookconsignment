import Link from 'next/link';
import { Suspense } from 'react';
import { AuthorsTable } from '../../components/authors/authors-table';

export default function AuthorsPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">Authors</h2>
          <p className="text-sm text-slate-400">
            Manage consignor relationships, onboarding requests, and agreement terms.
          </p>
        </div>
        <Link
          href="/authors/new"
          className="inline-flex h-10 items-center rounded-md bg-emerald-500 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
        >
          Add Author
        </Link>
      </header>
      <Suspense fallback={<div className="text-slate-400">Loading authors…</div>}>
        <AuthorsTable />
      </Suspense>
    </div>
  );
}

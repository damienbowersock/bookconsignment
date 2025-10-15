# BookConsign Monorepo

Multi-tenant consignment management platform for independent bookstores and authors. The codebase
is organized as a **Turborepo** with shared TypeScript packages so that web (Next.js), backend
(NestJS), and future mobile (Expo) clients stay in sync via end-to-end types.

## Stack Overview

- **Frontend:** Next.js 15 (App Router) + React 18, Tailwind CSS, React Query, Clerk (auth shell)
- **Backend:** NestJS 10 + tRPC, Prisma ORM, PostgreSQL with tenant-scoped models
- **Shared Packages:** Zod schemas, UI component kit (Tailwind + Radix-compatible), API SDK
- **Payments & Integrations:** Stripe Connect placeholders, POS ingestion adapters (Square first)
- **Infra Targets:** Vercel (web), Fly.io/Railway (API), Neon/Aiven (Postgres)

## Repository Layout

```
/apps
  /api        NestJS + tRPC service (Prisma, Stripe, Resend hooks)
  /web        Next.js App Router client for bookseller & author personas
  /mobile     Expo shell prepared for phase two

/packages
  /schemas    Zod models shared across API, web, mobile
  /lib        Currency, date, feature-flag utilities
  /ui         Tailwind design system + layout primitives
  /api-sdk    Typed tRPC client used by web/mobile

/apps/api/prisma
  schema.prisma   Data model with tenant_id on every row
  seed.ts         Demo workflow (tenant + inventory + sales + settlements)
```

Legacy Django assets remain untouched under `accounts/`, `catalog/`, etc. Remove them once the new
stack is fully adopted.

## Prerequisites

- Node.js 20+
- npm 10+ (workspaces enabled)
- PostgreSQL 14+ (local or managed)
- Stripe test account (for Connect onboarding simulation)
- Clerk (or Auth.js) project for authentication

## Environment Setup

1. **Install dependencies** (workspace aware):

   ```bash
   npm install
   npm run generate --workspace apps/api   # prisma generate
   ```

2. **Copy environment template** and set secrets:

   ```bash
   cp .env.example .env
   # Update DATABASE_URL, Clerk, Stripe keys, etc.
   ```

3. **Apply database migrations** (creates all tenant-scoped tables):

   ```bash
   npm run migrate:dev
   ```

4. **Seed demo data** (creates tenant, clerk user stub, author, inventory, sales, settlements):

   ```bash
   npm run seed
   ```

5. **Run the stack locally**

   ```bash
   npm run dev
   # Opens: web on http://localhost:3000, API on http://localhost:4000
   ```

   The dev script runs both web and API via Turbo in watch mode.

## CI & Quality Gates

- `npm run lint` — ESLint (root + workspace overrides)
- `npm run typecheck` — TypeScript project references
- `npm run test` — Jest (API) + Vitest (web, placeholders)
- `npm run build` — Compiled artifacts for deployment

GitHub Actions workflow definitions should run the commands above plus `npm run migrate:deploy`.

## Domain Highlights

- **Multi-tenancy:** `tenant_id` foreign key on every table. `TenancyService` resolves tenant via
  subdomain header or manual slug. Future RLS policies can be derived from the Prisma schema.
- **RBAC:** `UserTenant` join with enumerated roles (`BOOKSELLER_ADMIN`, `STAFF`, `AUTHOR`,
  `PLATFORM_ADMIN`). TRPC middleware enforces tenant scoping.
- **Consignment terms:** Effective-dated mappings (`ConsignmentTerm`, `TitleTerm`) with historical
  lookups applied during sales import and settlement generation.
- **Inventory & Sales:** Lot-based intake, stock adjustments, CSV/webhook-ready sales ingestion with
  idempotency. Inventory decrements atomically when sales import succeed.
- **Settlements & Payouts:** Period generation aggregates sale lines by author, creates immutable
  settlement lines, and leaves hooks for Stripe Connect payouts. Seed script demonstrates term
  changes mid-period and resulting statements.
- **Reporting:** Dashboard KPIs, top titles, liability, and settlement pipeline served via tRPC.
- **Notifications:** Placeholder router for Resend/SendGrid email templates scoped per tenant.

## Running Key Workflows

1. Seed script creates tenant `consignify`, admin user, author `Harper Winslow`, two titles, intake
   lots (qty 10 ea), seven sales across historical and updated terms, and generates current-period
   settlements.
2. Visit `/dashboard` to see aggregated KPIs, top titles, and pending settlements.
3. Visit `/authors` for roster management; `/settlements` exposes a generator action that triggers
   the tRPC pipeline and refreshes dashboard data.
4. Author portal (`/portal`) consumes the same tRPC contracts, ready for Clerk role-based routing.

## API Endpoints (tRPC)

Routers are composed under `/trpc`:

- `auth.me`, `auth.tenants`, `auth.switchTenant`
- `authors.list/create/update/requestLink/approveLink`
- `titles.list/create`
- `inventory.intake/lots/adjust`
- `sales.list/import`
- `settlements.generate/approve/lock/payout`
- `reports.overview`
- `notifications.test`

Shared schemas live in `packages/schemas`, ensuring type parity between client and server. The
`@bookconsign/api-sdk` package exposes a typed browser client consumed by Next.js via
`apps/web/lib/trpc-provider.tsx`.

## Mobile Next

- `apps/mobile` bootstraps an Expo 51 app that already depends on the shared API SDK and Zod
  schemas. Component primitives in `packages/ui` are React Native Web friendly, easing reuse.
- Barcode scanning (Expo `Camera` + `BarcodeScanner`) will be exposed through a shared hook in
  `packages/lib` so both web and mobile can share decoding logic.
- Focus next on Clerk OAuth integration for native clients, offline cache of inventory lots, and
  bridging POS adapters through background sync jobs.

## Observability & Ops

- Pino logging is configured in Nest; wire to OpenTelemetry exporters for traces/metrics.
- Add Sentry (browser + Node) via environment toggles.
- Background work (imports, settlement PDFs, Stripe transfers) can run via BullMQ in a future
  `jobs` workspace.

## Next Steps

1. Implement Clerk JWT validation inside `AuthService` and enforce RLS policies in Postgres.
2. Flesh out PDF rendering for intake receipts & settlement statements (React-PDF on the server).
3. Complete Stripe Connect onboarding + webhook handling under `apps/api/src/modules/payments`.
4. Build POS adapters starting with Square (webhook handler + SKU mapping UI).
5. Add Playwright happy-path E2E covering author onboarding → intake → sale import → settlement →
   payout.

---

Questions or feedback? Open an issue or drop a note in `docs/` once the handbook is added.

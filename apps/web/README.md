# AI Job Coach Web

The canonical frontend is a Next.js 15 application for the persisted Resume Agent workflow. `apps/web-legacy` remains the rollback target until production smoke checks pass.

## Local setup

Copy `.env.example` to `.env.local` and configure Clerk plus the Agent API origin. Then run:

```bash
npm ci
npm run dev
```

The application runs on `http://localhost:3001`. The Resume Agent is under `/dashboard/resume/agent`; the preserved coding-practice surface is under `/dashboard/leetcode`.

## Verification

```bash
npm run lint
npm run typecheck
npm run api:check
npm test -- --run
npm run build
```

Browser tests require valid Clerk test credentials and an authenticated Agent fixture service:

```bash
npm run test:e2e
```

## Cutover and rollback

Deploy `apps/web` alongside `apps/web-legacy`. Before switching traffic, verify sign-in return URLs, CORS, authenticated SSE, upload-to-export, downloads, direct run recovery, mobile drawers, and `/api/leetcode` in the production-like environment. Keep the legacy deployment address unchanged. Rolling back only switches frontend traffic to that address; persisted runs remain in the Agent backend and require no database rollback.

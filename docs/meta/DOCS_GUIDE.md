***REMOVED*** Documentation Guide (Conventions + Drift Prevention)

This repo has a lot of moving pieces. These conventions keep docs consistent and reduce “doc drift”.

***REMOVED******REMOVED*** Canonical entrypoints

- **Start here (new devs)**: `docs/getting-started/ONBOARDING.md`
- **Service map**: `docs/getting-started/SERVICE_MAP.md`
- **Infra canonical pointers**: `infra/README.md`

***REMOVED******REMOVED*** Docker Compose conventions

- Prefer **Compose v2**:
  - Use `docker compose ...`
  - Only mention `docker-compose` as a fallback in scripts intended for older hosts.
- Prefer referencing compose files under:
  - `infra/compose/prod.yml`
  - `infra/compose/monitoring.yml`
  - `infra/compose/monitoring.local.yml`
  - `infra/compose/kafka.local.yml`

***REMOVED******REMOVED*** Environment file conventions

- Templates live under `infra/env/*.example` and are committed.
- Real environment files (filled with secrets) should **not** be committed.

Common templates:

- App stack: `infra/env/prod.example` → copy to `.env.prod` at repo root
- Monitoring stack: `infra/env/monitoring.prod.example` → copy to `infra/.env.monitoring.prod`
- Dev example: `infra/env/development.example`

For local dev, prefer **per-service** env files where supported:

- `apps/<service>/.env` or `apps/<service>/.env.local`

***REMOVED******REMOVED*** Linking rules

- If you mention an app/library, link to its README:
  - `apps/<service>/README.md`, `libs/<lib>/README.md`
- If you mention infra compose/env files, link to:
  - `infra/compose/*`, `infra/env/*`

***REMOVED******REMOVED*** “If you change X, update Y” checklist

When you change **infra paths**, **compose filenames**, or **env template locations**, update:

- `README.md` (quick start + docs index)
- `docs/getting-started/ONBOARDING.md`
- `docs/getting-started/SERVICE_MAP.md`
- `infra/README.md`
- Any affected docs under `docs/` (deployment/monitoring/tracing guides)
- Any scripts that print or execute compose commands under `infra/scripts/` and `scripts/`

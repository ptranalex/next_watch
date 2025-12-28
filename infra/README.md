***REMOVED******REMOVED*** infra/

This folder contains **deployment**, **monitoring**, and **developer tooling** for the NextWatch monorepo.

***REMOVED******REMOVED******REMOVED*** Canonical entrypoints

- **Production app stack (Docker Compose)**: `infra/compose/prod.yml`
- **Monitoring stack (Docker Compose)**: `infra/compose/monitoring.yml`
- **Monitoring stack (local dev)**: `infra/compose/monitoring.local.yml`
- **Kafka stack (local dev)**: `infra/compose/kafka.local.yml`

***REMOVED******REMOVED******REMOVED*** Environment templates (copy → fill → do not commit)

- **App stack**: `infra/env/prod.example` → copy to `.env.prod` at repo root
- **Monitoring stack**: `infra/env/monitoring.prod.example` → copy to `infra/.env.monitoring.prod`
- **Grafana Cloud (Alloy) credentials**: `infra/monitoring/alloy/.env.example` → copy values into `.env.prod` (used by `grafana-alloy` in `infra/compose/prod.yml`)

***REMOVED******REMOVED******REMOVED*** Scripts

- **Local monitoring deploy**: `infra/scripts/deploy-monitoring-local.sh`
- **Service status checks**: `infra/scripts/check-services.sh`
- **tmux dev environment**: `infra/tmux/start_services_tmux.sh`
- **AWS monitoring deployment**: `infra/aws/deployment/deploy-monitoring-one-click.sh`

***REMOVED******REMOVED******REMOVED*** Conventions

- Prefer running compose from **repo root**:
  - `docker compose -f infra/compose/prod.yml --env-file .env.prod up -d`
  - `docker compose -f infra/compose/monitoring.yml --env-file infra/.env.monitoring.prod up -d`
- Do **not** commit real environment files (only `*.example` templates should be tracked).

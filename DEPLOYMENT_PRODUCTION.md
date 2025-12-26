***REMOVED*** Production Deployment Guide

Complete guide for deploying Next Watch to production with proper security configuration.

***REMOVED******REMOVED*** Prerequisites

- Docker & Docker Compose installed
- PostgreSQL database (local or hosted)
- Redis instance (local or hosted)
- Domain name with DNS configured
- SSL certificates (via Let's Encrypt or provider)

***REMOVED******REMOVED*** 1. Initial Setup

***REMOVED******REMOVED******REMOVED*** Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/next_watch.git
cd next_watch
```

***REMOVED******REMOVED******REMOVED*** Create Production Environment File

```bash
***REMOVED*** Copy the template
cp .env.production.local.example .env.production.local

***REMOVED*** Edit with your values
nano .env.production.local
```

***REMOVED******REMOVED*** 2. Configure Required Secrets

***REMOVED******REMOVED******REMOVED*** Generate Strong Secrets

```bash
***REMOVED*** JWT Secret (required)
openssl rand -base64 32

***REMOVED*** Internal API Key (required)
openssl rand -base64 32

***REMOVED*** Grafana Secret Key (if self-hosting)
openssl rand -base64 32
```

***REMOVED******REMOVED******REMOVED*** Set Production Domain

```env
PRODUCTION_DOMAIN=your-domain.com
NEXT_PUBLIC_BFF_API_URL=https://your-domain.com
```

***REMOVED******REMOVED******REMOVED*** Configure Database

```env
POSTGRES_USER=next_watch_prod
POSTGRES_PASSWORD=<strong-password-here>
POSTGRES_DB=next_watch
```

***REMOVED******REMOVED*** 3. External API Keys (Optional)

***REMOVED******REMOVED******REMOVED*** TMDB API (for movie data import)

1. Create account at https://www.themoviedb.org
2. Go to Settings → API
3. Request API key
4. Add to `.env.production.local`:

```env
TMDB_ACCESS_TOKEN=your-token-here
```

***REMOVED******REMOVED******REMOVED*** OMDB API (for additional movie data)

1. Get key from http://www.omdbapi.com/apikey.aspx
2. Add to `.env.production.local`:

```env
OMDB_API_KEY=your-key-here
```

***REMOVED******REMOVED******REMOVED*** Google OAuth (for social login)

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add authorized origins: `https://your-domain.com`
4. Add to `.env.production.local`:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

***REMOVED******REMOVED*** 4. Observability Setup (Optional)

***REMOVED******REMOVED******REMOVED*** Grafana Cloud

1. Sign up at https://grafana.com
2. Create a stack
3. Get credentials from: Your Stack → Configuration → Data Sources

**Prometheus (Metrics)**:
```env
GRAFANA_CLOUD_METRICS_URL=https://prometheus-prod-XX...
GRAFANA_CLOUD_METRICS_USERNAME=your-username
GRAFANA_CLOUD_METRICS_PASSWORD=your-api-key
```

**Loki (Logs)**:
```env
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-XXX...
GRAFANA_CLOUD_LOGS_USERNAME=your-username
GRAFANA_CLOUD_LOGS_PASSWORD=your-api-key
```

**Tempo (Traces)**:
```env
GRAFANA_CLOUD_TRACES_URL=https://tempo-prod-XX...
GRAFANA_CLOUD_TRACES_USERNAME=your-username
GRAFANA_CLOUD_TRACES_PASSWORD=your-api-key
```

***REMOVED******REMOVED******REMOVED*** Self-Hosted Monitoring

If self-hosting Grafana:

```env
GRAFANA_ADMIN_PASSWORD=<strong-password>
GRAFANA_DB_PASSWORD=<strong-password>
GRAFANA_SECRET_KEY=<generated-with-openssl>
```

***REMOVED******REMOVED*** 5. Build Docker Images

```bash
***REMOVED*** Build all services
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest .
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest .
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest .
docker build -f apps/recommendation-api/Dockerfile -t next-watch-recommendation:latest .
docker build -f apps/ml-api/Dockerfile -t next-watch-ml:latest .
docker build -f apps/search-api/Dockerfile -t next-watch-search:latest .
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest .
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest .
```

Or use the provided script:

```bash
chmod +x scripts/deploy-prod.sh
./scripts/deploy-prod.sh --build-only
```

***REMOVED******REMOVED*** 6. Deploy Services

```bash
***REMOVED*** Start all services
docker-compose -f infra/docker-compose.prod.yml --env-file .env.production.local up -d

***REMOVED*** Check status
docker ps

***REMOVED*** View logs
docker-compose -f infra/docker-compose.prod.yml logs -f
```

***REMOVED******REMOVED*** 7. Initial Data Import (Optional)

```bash
***REMOVED*** Import movie data from TMDB
docker run --rm \
  --env-file .env.production.local \
  --network host \
  next-watch-importer:latest \
  python -m data_importer.cli sync --verbose
```

***REMOVED******REMOVED*** 8. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/nextwatch`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ***REMOVED*** Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    ***REMOVED*** BFF API
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    ***REMOVED*** Grafana (if self-hosting)
    location /grafana/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_set_header Host $host;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/nextwatch /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

***REMOVED******REMOVED*** 9. SSL Certificate Setup

Using Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

***REMOVED******REMOVED*** 10. Health Checks

Verify all services are running:

```bash
***REMOVED*** Backend API
curl https://your-domain.com/api/health

***REMOVED*** Frontend
curl https://your-domain.com

***REMOVED*** Check all containers
docker ps
```

***REMOVED******REMOVED*** 11. Monitoring Access

Access your monitoring:

- **Grafana**: https://your-domain.com/grafana/
- **Prometheus**: https://your-domain.com/prometheus/
- **Application**: https://your-domain.com

***REMOVED******REMOVED*** Security Checklist

Before going live:

- [ ] All secrets generated with strong random values
- [ ] Database passwords are strong and unique
- [ ] JWT_SECRET is at least 32 characters
- [ ] INTERNAL_API_KEY is unique and random
- [ ] SSL certificates are valid and auto-renewing
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Services bind to localhost (not 0.0.0.0)
- [ ] Nginx reverse proxy configured
- [ ] CORS origins restricted to your domain
- [ ] .env files are NOT in git (check .gitignore)
- [ ] Monitoring/alerting configured
- [ ] Backups configured for database
- [ ] Rate limiting enabled

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Services won't start

```bash
***REMOVED*** Check logs
docker-compose -f infra/docker-compose.prod.yml logs

***REMOVED*** Check environment variables
docker-compose -f infra/docker-compose.prod.yml config
```

***REMOVED******REMOVED******REMOVED*** Database connection errors

```bash
***REMOVED*** Verify database is accessible
psql -h localhost -U your_user -d next_watch

***REMOVED*** Check connection string in .env.production.local
```

***REMOVED******REMOVED******REMOVED*** API returns 502 Bad Gateway

```bash
***REMOVED*** Check if backend services are running
docker ps | grep next-watch

***REMOVED*** Check nginx error log
sudo tail -f /var/log/nginx/error.log
```

***REMOVED******REMOVED*** Maintenance

***REMOVED******REMOVED******REMOVED*** Update Deployment

```bash
***REMOVED*** Pull latest code
git pull origin main

***REMOVED*** Rebuild images
./scripts/deploy-prod.sh

***REMOVED*** Restart services
docker-compose -f infra/docker-compose.prod.yml restart
```

***REMOVED******REMOVED******REMOVED*** Backup Database

```bash
***REMOVED*** Create backup
pg_dump -h localhost -U your_user next_watch > backup_$(date +%Y%m%d).sql

***REMOVED*** Restore backup
psql -h localhost -U your_user next_watch < backup_20240101.sql
```

***REMOVED******REMOVED******REMOVED*** View Logs

```bash
***REMOVED*** All services
docker-compose -f infra/docker-compose.prod.yml logs -f

***REMOVED*** Specific service
docker logs -f backend-api
```

***REMOVED******REMOVED*** Support

For issues or questions:
- Check documentation in `/docs`
- Review service-specific READMEs in `/apps`
- Open an issue on GitHub

***REMOVED******REMOVED*** License

MIT License - see LICENSE file for details


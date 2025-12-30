# Secure Nginx Routing Configuration

## Recommended Approach: BFF-Only External Access

All external API traffic goes through the BFF service only. Auth and Backend services are internal-only.

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name your-domain.com www.your-domain.com;

    # SSL configuration...
    ssl_certificate /etc/ssl/certs/cloudflare-origin.pem;
    ssl_certificate_key /etc/ssl/private/cloudflare-origin.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # All BFF traffic (what frontend actually calls)
    location /bff/ {
        proxy_pass http://localhost:8001/bff/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MONITORING ACCESS (Production Addition)
    # Restrict to admin IPs only in production
    location /grafana/ {
        # Optional: Restrict by IP
        # allow 192.168.1.0/24;
        # deny all;

        proxy_pass http://localhost:3001/grafana/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Grafana WebSocket support
    location /grafana/api/live/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_pass http://localhost:3001/;
    }

    location /prometheus/ {
        # Optional: Restrict by IP
        # allow 192.168.1.0/24;
        # deny all;

        proxy_pass http://localhost:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Architecture

### External Access (via nginx):

- ✅ **Frontend** (`/`) → Next.js (port 3000)
- ✅ **BFF APIs** (`/bff/`) → BFF service (port 8001)

### Internal Service Communication:

- 🔒 **BFF** → Auth API (port 8003) - Internal only
- 🔒 **BFF** → Backend API (port 8000) - Internal only
- 🔒 **Auth & Backend** - No external access

### Benefits:

1. **🛡️ Security** - Single entry point, no direct service exposure
2. **🎯 Centralized** - All external requests go through BFF
3. **🔐 Internal Services** - Auth and Backend are protected
4. **📊 Monitoring** - Easy to monitor all external traffic
5. **🚦 Rate Limiting** - Apply limits at single point (BFF)

## 🚨 **Production Security Recommendations**

### **Critical: Docker Network Binding**

Current services bind to `0.0.0.0:*` (all interfaces). For maximum security:

```yaml
# docker-compose.yml - Bind to localhost only
services:
  backend-api:
    ports:
      - "127.0.0.1:8000:8000" # Instead of "8000:8000"

  auth-api:
    ports:
      - "127.0.0.1:8003:8003" # Instead of "8003:8003"
```

### **Monitoring Access Control**

Add IP restrictions for monitoring endpoints:

```nginx
location /grafana/ {
    # Restrict to admin IPs
    allow 192.168.1.0/24;    # Internal network
    allow 10.0.0.0/8;        # VPN range
    deny all;

    proxy_pass http://localhost:3001/grafana/;
    # ... headers
}
```

### **Additional Security Headers**

```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### **Rate Limiting**

```nginx
# Add rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /bff/ {
    limit_req zone=api burst=20 nodelay;
    # ... proxy configuration
}
```

### URL Examples:

**Application URLs:**

- `https://your-domain.com/bff/v1/movies` → BFF handles movies
- `https://your-domain.com/bff/v1/auth/login` → BFF proxies to Auth
- `https://your-domain.com/bff/health` → BFF health check
- ❌ Direct service access → Not accessible (secure)

**Monitoring URLs (Admin Only):**

- `https://your-domain.com/grafana/` → Grafana dashboard
- `https://your-domain.com/prometheus/` → Prometheus metrics
- ⚠️ Consider IP restrictions for production

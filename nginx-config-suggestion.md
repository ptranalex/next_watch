***REMOVED*** Secure Nginx Routing Configuration

***REMOVED******REMOVED*** Recommended Approach: BFF-Only External Access

All external API traffic goes through the BFF service only. Auth and Backend services are internal-only.

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name alexsandbox.me www.alexsandbox.me;

    ***REMOVED*** SSL configuration...
    ssl_certificate /etc/ssl/certs/cloudflare-origin.pem;
    ssl_certificate_key /etc/ssl/private/cloudflare-origin.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    ***REMOVED*** All BFF traffic (what frontend actually calls)
    location /bff/ {
        proxy_pass http://localhost:8001/bff/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    ***REMOVED*** Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

***REMOVED******REMOVED*** Security Architecture

***REMOVED******REMOVED******REMOVED*** External Access (via nginx):

- ✅ **Frontend** (`/`) → Next.js (port 3000)
- ✅ **BFF APIs** (`/bff/`) → BFF service (port 8001)

***REMOVED******REMOVED******REMOVED*** Internal Service Communication:

- 🔒 **BFF** → Auth API (port 8003) - Internal only
- 🔒 **BFF** → Backend API (port 8000) - Internal only
- 🔒 **Auth & Backend** - No external access

***REMOVED******REMOVED******REMOVED*** Benefits:

1. **🛡️ Security** - Single entry point, no direct service exposure
2. **🎯 Centralized** - All external requests go through BFF
3. **🔐 Internal Services** - Auth and Backend are protected
4. **📊 Monitoring** - Easy to monitor all external traffic
5. **🚦 Rate Limiting** - Apply limits at single point (BFF)

***REMOVED******REMOVED******REMOVED*** URL Examples:

- `https://alexsandbox.me/bff/v1/movies` → BFF handles movies
- `https://alexsandbox.me/bff/v1/auth/login` → BFF proxies to Auth
- `https://alexsandbox.me/bff/health` → BFF health check
- ❌ Direct service access → Not accessible (secure)

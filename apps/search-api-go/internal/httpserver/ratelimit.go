package httpserver

import (
	"net"
	"net/http"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

type fixedWindowLimit struct {
	Requests int
	Window   time.Duration
}

type fixedWindowBucket struct {
	Count   int
	ResetAt time.Time
}

type FixedWindowIPLimiter struct {
	defaultLimit fixedWindowLimit
	overrides    map[string]fixedWindowLimit // exact path -> limit

	exemptIPs   map[string]struct{}
	exemptCIDRs []*net.IPNet

	mu      sync.Mutex
	buckets map[string]fixedWindowBucket

	reqs uint64
}

func newSearchRateLimiter(env string) *FixedWindowIPLimiter {
	// Mirrors the Python Search API protections (see apps/search-api/src/search_api/core/app_fast_core.py).
	overrides := map[string]fixedWindowLimit{
		"/api/v1/search":                  {Requests: 100, Window: 60 * time.Second},
		"/api/v1/search/suggestions":      {Requests: 200, Window: 60 * time.Second},
		"/api/v1/search/suggestions/text": {Requests: 200, Window: 60 * time.Second},
		"/api/v1/search/all":              {Requests: 50, Window: 60 * time.Second},
		"/health":                         {Requests: 1000, Window: 60 * time.Second},
		"/metrics":                        {Requests: 1000, Window: 60 * time.Second},
	}

	def := fixedWindowLimit{Requests: 1000, Window: 60 * time.Second}
	if env == "prod" || env == "production" {
		// Align with fast-core default_limit="300/hour" in production.
		def = fixedWindowLimit{Requests: 300, Window: 60 * time.Minute}
	} else {
		// Align with fast-core default_limit="1000/hour" in non-prod.
		def = fixedWindowLimit{Requests: 1000, Window: 60 * time.Minute}
	}

	exemptIPs := []string{"127.0.0.1", "::1"}
	exemptCIDRs := []string{}
	if env != "prod" && env != "production" {
		exemptCIDRs = []string{"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"}
	}

	return NewFixedWindowIPLimiter(def, overrides, exemptIPs, exemptCIDRs)
}

func NewFixedWindowIPLimiter(def fixedWindowLimit, overrides map[string]fixedWindowLimit, exemptIPs []string, exemptCIDRs []string) *FixedWindowIPLimiter {
	l := &FixedWindowIPLimiter{
		defaultLimit: def,
		overrides:    overrides,
		exemptIPs:    make(map[string]struct{}, len(exemptIPs)),
		exemptCIDRs:  make([]*net.IPNet, 0, len(exemptCIDRs)),
		buckets:      make(map[string]fixedWindowBucket, 1024),
	}
	for _, ip := range exemptIPs {
		if ip != "" {
			l.exemptIPs[ip] = struct{}{}
		}
	}
	for _, cidr := range exemptCIDRs {
		_, n, err := net.ParseCIDR(cidr)
		if err == nil && n != nil {
			l.exemptCIDRs = append(l.exemptCIDRs, n)
		}
	}
	return l
}

func (l *FixedWindowIPLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ip := realIP(r)
		if l.isExemptIP(ip) {
			next.ServeHTTP(w, r)
			return
		}

		limit := l.limitForPath(r.URL.Path)
		if limit.Requests <= 0 || limit.Window <= 0 {
			next.ServeHTTP(w, r)
			return
		}

		allowed, remaining, resetAt := l.allow(ip, r.URL.Path, limit)

		w.Header().Set("X-RateLimit-Limit", strconv.Itoa(limit.Requests))
		w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(remaining))
		w.Header().Set("X-RateLimit-Reset", strconv.FormatInt(resetAt.Unix(), 10))

		if !allowed {
			retryAfter := int(time.Until(resetAt).Seconds())
			if retryAfter < 0 {
				retryAfter = 0
			}
			w.Header().Set("Retry-After", strconv.Itoa(retryAfter))
			writeJSONError(w, http.StatusTooManyRequests, "Rate limit exceeded")
			return
		}

		next.ServeHTTP(w, r)
	})
}

func (l *FixedWindowIPLimiter) limitForPath(path string) fixedWindowLimit {
	if v, ok := l.overrides[path]; ok {
		return v
	}
	return l.defaultLimit
}

func (l *FixedWindowIPLimiter) isExemptIP(ip string) bool {
	if ip == "" {
		return false
	}
	if _, ok := l.exemptIPs[ip]; ok {
		return true
	}
	parsed := net.ParseIP(ip)
	if parsed == nil {
		return false
	}
	for _, n := range l.exemptCIDRs {
		if n.Contains(parsed) {
			return true
		}
	}
	return false
}

func (l *FixedWindowIPLimiter) allow(ip, path string, limit fixedWindowLimit) (allowed bool, remaining int, resetAt time.Time) {
	now := time.Now()
	key := ip + "|" + path

	l.mu.Lock()
	defer l.mu.Unlock()

	// Opportunistic cleanup every ~1024 requests.
	if atomic.AddUint64(&l.reqs, 1)%1024 == 0 {
		for k, b := range l.buckets {
			if now.After(b.ResetAt) {
				delete(l.buckets, k)
			}
		}
	}

	b, ok := l.buckets[key]
	if !ok || now.After(b.ResetAt) {
		b = fixedWindowBucket{Count: 0, ResetAt: now.Add(limit.Window)}
	}

	if b.Count >= limit.Requests {
		remaining = 0
		return false, remaining, b.ResetAt
	}

	b.Count++
	l.buckets[key] = b

	remaining = limit.Requests - b.Count
	if remaining < 0 {
		remaining = 0
	}
	return true, remaining, b.ResetAt
}

package httpserver

import (
	"encoding/json"
	"net"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/rs/zerolog/log"
)

type Server struct {
	HTTP *http.Server
}

type Options struct {
	Addr         string
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
	Env          string

	EnableMetrics    bool
	EnableRateLimits bool

	HealthHandler http.Handler
	// APIV1Router allows wiring versioned endpoints under /api/v1/*.
	// If nil, /api/v1 returns 501 Not Implemented.
	APIV1Router func(r chi.Router)
}

func New(opts Options) *Server {
	r := chi.NewRouter()

	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Recoverer)

	if opts.EnableMetrics {
		r.Handle("/metrics", metricsHandler())
	}

	r.Use(requestLogger(opts.Env))

	if opts.EnableMetrics {
		r.Use(metricsMiddleware())
	}

	if opts.EnableRateLimits {
		limiter := newSearchRateLimiter(opts.Env)
		r.Use(limiter.Middleware)
	}

	r.Get("/health", func(w http.ResponseWriter, req *http.Request) {
		if opts.HealthHandler == nil {
			w.WriteHeader(http.StatusNotImplemented)
			return
		}
		opts.HealthHandler.ServeHTTP(w, req)
	})

	r.Route("/api/v1", func(v1 chi.Router) {
		if opts.APIV1Router != nil {
			opts.APIV1Router(v1)
			return
		}
		v1.NotFound(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotImplemented)
		})
	})

	srv := &http.Server{
		Addr:              opts.Addr,
		Handler:           r,
		ReadTimeout:       opts.ReadTimeout,
		WriteTimeout:      opts.WriteTimeout,
		IdleTimeout:       opts.IdleTimeout,
		ReadHeaderTimeout: 5 * time.Second,
	}

	return &Server{HTTP: srv}
}

func requestLogger(env string) func(next http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
			start := time.Now()

			next.ServeHTTP(ww, r)

			status := ww.Status()
			if status == 0 {
				status = http.StatusOK
			}

			route := ""
			if rc := chi.RouteContext(r.Context()); rc != nil {
				route = rc.RoutePattern()
			}
			if route == "" {
				route = r.URL.Path
			}

			ev := log.Info()
			if status >= 500 {
				ev = log.Error()
			} else if status >= 400 {
				ev = log.Warn()
			}

			ev.
				Str("method", r.Method).
				Str("path", r.URL.Path).
				Str("route", route).
				Str("request_id", middleware.GetReqID(r.Context())).
				Str("remote_ip", realIP(r)).
				Int("status", status).
				Int("bytes", ww.BytesWritten()).
				Dur("duration", time.Since(start)).
				Str("user_agent", userAgentForEnv(env, r)).
				Msg("http request")
		})
	}
}

func userAgentForEnv(env string, r *http.Request) string {
	// Keep production logs leaner.
	if env == "prod" || env == "production" {
		return ""
	}
	return r.UserAgent()
}

func realIP(r *http.Request) string {
	// chi middleware.RealIP overwrites RemoteAddr with the parsed IP string when possible.
	// Still defensively handle host:port formats.
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err == nil && host != "" {
		return host
	}
	return r.RemoteAddr
}

func writeJSONError(w http.ResponseWriter, status int, detail string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]any{"detail": detail})
}

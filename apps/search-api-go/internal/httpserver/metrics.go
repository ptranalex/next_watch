package httpserver

import (
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	httpInFlight = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "http_requests_in_flight",
		Help: "Current number of in-flight HTTP requests.",
	})
	httpRequestsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "http_requests_total",
		Help: "Total number of HTTP requests processed.",
	}, []string{"method", "route", "status"})
	httpRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "http_request_duration_seconds",
		Help:    "HTTP request duration in seconds.",
		Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10},
	}, []string{"method", "route", "status"})
)

func metricsHandler() http.Handler {
	return promhttp.Handler()
}

func metricsMiddleware() func(next http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Avoid self-scrape recursion and keep metrics clean.
			if r.URL.Path == "/metrics" || r.Method == http.MethodOptions {
				next.ServeHTTP(w, r)
				return
			}

			start := time.Now()
			httpInFlight.Inc()
			defer httpInFlight.Dec()

			ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
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

			labelsRoute := route
			labelsStatus := strconv.Itoa(status)
			httpRequestsTotal.WithLabelValues(r.Method, labelsRoute, labelsStatus).Inc()
			httpRequestDuration.WithLabelValues(r.Method, labelsRoute, labelsStatus).Observe(time.Since(start).Seconds())
		})
	}
}

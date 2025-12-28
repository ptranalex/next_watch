package health

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/rs/zerolog/log"
)

type RedisPinger interface {
	Ping(ctx context.Context) (time.Duration, error)
}

type Handler struct {
	Service string
	Env     string

	Version string
	Commit  string

	RedisEnabled bool
	Redis        RedisPinger
}

func (h Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	type redisStatus struct {
		Enabled   bool   `json:"enabled"`
		OK        bool   `json:"ok"`
		LatencyMs int64  `json:"latency_ms,omitempty"`
		Error     string `json:"error,omitempty"`
	}
	type response struct {
		Status  string      `json:"status"`
		Service string      `json:"service"`
		Env     string      `json:"env"`
		Version string      `json:"version,omitempty"`
		Commit  string      `json:"commit,omitempty"`
		Time    string      `json:"time"`
		Redis   redisStatus `json:"redis"`
	}

	resp := response{
		Status:  "ok",
		Service: h.Service,
		Env:     h.Env,
		Version: h.Version,
		Commit:  h.Commit,
		Time:    time.Now().UTC().Format(time.RFC3339Nano),
		Redis: redisStatus{
			Enabled: h.RedisEnabled,
			OK:      true,
		},
	}

	statusCode := http.StatusOK

	if h.RedisEnabled {
		ctx, cancel := context.WithTimeout(r.Context(), 750*time.Millisecond)
		defer cancel()

		latency, err := h.Redis.Ping(ctx)
		if err != nil {
			resp.Status = "degraded"
			resp.Redis.OK = false
			resp.Redis.Error = err.Error()
			statusCode = http.StatusServiceUnavailable
			log.Warn().Err(err).Msg("health redis ping failed")
		} else {
			resp.Redis.OK = true
			resp.Redis.LatencyMs = latency.Milliseconds()
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	_ = json.NewEncoder(w).Encode(resp)
}

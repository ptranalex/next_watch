package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog/log"

	"github.com/next-watch/search-api-go/internal/api/health"
	"github.com/next-watch/search-api-go/internal/api/search"
	"github.com/next-watch/search-api-go/internal/config"
	"github.com/next-watch/search-api-go/internal/httpserver"
	"github.com/next-watch/search-api-go/internal/indexer"
	"github.com/next-watch/search-api-go/internal/logging"
	"github.com/next-watch/search-api-go/internal/redisclient"
)

// overridden via -ldflags at build time
var (
	version = "dev"
	commit  = "none"
)

func main() {
	cfg := config.Load()

	logging.Setup(logging.Options{
		Env:      cfg.Env,
		Level:    cfg.LogLevel,
		Service:  cfg.ServiceName,
		UseColor: cfg.Env == "dev",
	})

	var redis *redisclient.Client
	var err error
	redisEnabled := cfg.RedisURL != ""
	if redisEnabled {
		redis, err = redisclient.New(cfg.RedisURL)
		if err != nil {
			log.Fatal().Err(err).Msg("failed to init redis client")
		}
		defer func() { _ = redis.Close() }()
	}

	var store *indexer.RedisV2Store
	if redisEnabled {
		store, err = indexer.NewRedisV2Store(indexer.RedisV2StoreOptions{
			RedisURL: cfg.RedisURL,
			Prefix:   cfg.SearchV2KeyPrefix,
		})
		if err != nil {
			log.Fatal().Err(err).Msg("failed to init redis v2 store")
		}
		defer func() { _ = store.Close() }()
	}

	healthHandler := health.Handler{
		Service:      cfg.ServiceName,
		Env:          cfg.Env,
		Version:      version,
		Commit:       commit,
		RedisEnabled: redisEnabled,
		Redis:        redis,
	}

	searchHandler := search.Handler{Store: store}

	srv := httpserver.New(httpserver.Options{
		Addr:             ":" + cfg.Port,
		ReadTimeout:      cfg.ReadTimeout,
		WriteTimeout:     cfg.WriteTimeout,
		IdleTimeout:      cfg.IdleTimeout,
		Env:              cfg.Env,
		EnableMetrics:    cfg.EnableMetrics,
		EnableRateLimits: cfg.EnableRateLimits,
		HealthHandler:    healthHandler,
		APIV1Router: func(r chi.Router) {
			searchHandler.Routes(r)
		},
	})

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	go func() {
		log.Info().
			Str("addr", srv.HTTP.Addr).
			Str("version", version).
			Str("commit", commit).
			Msg("search-api-go started")

		if err := srv.HTTP.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("http server failed")
		}
	}()

	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	log.Info().Msg("shutting down")
	if err := srv.HTTP.Shutdown(shutdownCtx); err != nil {
		log.Error().Err(err).Msg("http shutdown error")
	}
}

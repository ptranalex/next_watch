package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/rs/zerolog/log"

	"github.com/next-watch/search-api-go/internal/backend"
	"github.com/next-watch/search-api-go/internal/config"
	"github.com/next-watch/search-api-go/internal/indexer"
	"github.com/next-watch/search-api-go/internal/logging"
)

// Usage:
//   REDIS_URL=redis://localhost:6379/0 BACKEND_API_URL=http://localhost:8000 go run ./cmd/search-indexer --clear
func main() {
	cfg := config.Load()

	logging.Setup(logging.Options{
		Env:      cfg.Env,
		Level:    cfg.LogLevel,
		Service:  "search-indexer-go",
		UseColor: cfg.Env == "dev",
	})

	var (
		redisURL  = flag.String("redis-url", cfg.RedisURL, "Redis URL (required). e.g. redis://localhost:6379/0")
		backendURL = flag.String("backend-url", cfg.BackendAPIURL, "Backend API base URL. e.g. http://localhost:8000")
		internalAPIKey = flag.String("internal-api-key", cfg.InternalAPIKey, "Optional internal API key (sent as Internal-API-Key)")

		prefix = flag.String("prefix", cfg.SearchV2KeyPrefix, "Redis key prefix for v2 schema (default: search:v2)")

		clear = flag.Bool("clear", false, "Clear existing v2 keys for prefix before indexing")

		movies = flag.Bool("movies", true, "Index movies")
		actors = flag.Bool("actors", true, "Index actors")

		moviesLimit = flag.Int("movies-limit", 0, "Max movies to fetch (0 = all, bounded by max-pages)")
		actorsLimit = flag.Int("actors-limit", 0, "Max actors to fetch (0 = all, bounded by max-pages)")

		includeWords  = flag.Bool("include-words", true, "For movies, index individual words + short prefixes (for better partial matching)")
		minWordLen    = flag.Int("min-word-length", 3, "Minimum word length when include-words is enabled")
		batchSize     = flag.Int("batch-size", 100, "Redis pipeline flush batch size (entities)")
		maxPages      = flag.Int("max-pages", 200, "Max pages to fetch from Backend API (safety cap)")
		requestTimeout = flag.Duration("request-timeout", cfg.BackendAPITimeout, "Backend API request timeout (e.g. 30s)")
	)

	flag.Parse()

	if *redisURL == "" {
		log.Fatal().Msg("REDIS_URL (or --redis-url) is required")
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	store, err := indexer.NewRedisV2Store(indexer.RedisV2StoreOptions{
		RedisURL: *redisURL,
		Prefix:   *prefix,
	})
	if err != nil {
		log.Fatal().Err(err).Msg("failed to init redis v2 store")
	}
	defer func() { _ = store.Close() }()

	if err := store.Ping(ctx); err != nil {
		log.Fatal().Err(err).Msg("redis ping failed")
	}

	be := backend.New(*backendURL, *requestTimeout, *internalAPIKey)

	r := indexer.Runner{
		Backend: be,
		Store:   store,
	}

	if *clear {
		log.Info().
			Str("prefix", *prefix).
			Msg("clearing existing v2 keys")

		clearCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
		deleted, err := store.ClearPrefix(clearCtx, 1000)
		cancel()
		if err != nil {
			log.Fatal().Err(err).Msg("failed to clear v2 keys")
		}
		log.Info().Int64("deleted_keys", deleted).Msg("clear complete")
	}

	log.Info().
		Str("backend_url", *backendURL).
		Str("prefix", *prefix).
		Bool("movies", *movies).
		Bool("actors", *actors).
		Int("movies_limit", *moviesLimit).
		Int("actors_limit", *actorsLimit).
		Msg("starting indexing")

	st, err := r.Run(ctx, indexer.Options{
		MoviesLimit:   *moviesLimit,
		ActorsLimit:   *actorsLimit,
		IncludeMovies: *movies,
		IncludeActors: *actors,
		IncludeWords:  *includeWords,
		MinWordLength: *minWordLen,
		BatchSize:     *batchSize,
		MaxPages:      *maxPages,
		RequestTimeout: *requestTimeout,
	})
	if err != nil {
		log.Fatal().Err(err).Msg("indexing failed")
	}

	counts, err := store.Counts(ctx)
	if err != nil {
		log.Fatal().Err(err).Msg("failed to read redis counts")
	}

	log.Info().
		Int("movies_fetched", st.MoviesFetched).
		Int("movies_indexed", st.MoviesIndexed).
		Int("actors_fetched", st.ActorsFetched).
		Int("actors_indexed", st.ActorsIndexed).
		Int64("movie_suggestions", counts.MovieSuggestions).
		Int64("actor_suggestions", counts.ActorSuggestions).
		Int64("entities", counts.Entities).
		Msg("indexing complete")
}

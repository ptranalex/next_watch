package indexer

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/next-watch/search-api-go/internal/backend"
)

type Options struct {
	MoviesLimit int // 0 means "all (bounded by max pages)"
	ActorsLimit int // 0 means "all (bounded by max pages)"

	IncludeMovies bool
	IncludeActors bool

	IncludeWords  bool
	MinWordLength int

	BatchSize int
	MaxPages  int

	RequestTimeout time.Duration
}

type Stats struct {
	MoviesFetched int
	ActorsFetched int

	MoviesIndexed int
	ActorsIndexed int
}

type Runner struct {
	Backend *backend.Client
	Store   *RedisV2Store
}

func (r *Runner) Run(ctx context.Context, opts Options) (Stats, error) {
	var st Stats
	if r == nil || r.Backend == nil || r.Store == nil {
		return st, fmt.Errorf("indexer: backend client and redis store are required")
	}
	if opts.BatchSize <= 0 {
		opts.BatchSize = 100
	}
	if opts.MaxPages <= 0 {
		opts.MaxPages = 200
	}
	if opts.MinWordLength <= 0 {
		opts.MinWordLength = 3
	}
	if opts.RequestTimeout <= 0 {
		opts.RequestTimeout = 30 * time.Second
	}

	if opts.IncludeMovies {
		movies, err := r.fetchMovies(ctx, opts.MoviesLimit, opts.MaxPages, opts.RequestTimeout)
		if err != nil {
			return st, err
		}
		st.MoviesFetched = len(movies)

		records := make([]MovieRecord, 0, len(movies))
		for _, m := range movies {
			rec, ok := mapMovie(m)
			if !ok {
				continue
			}
			records = append(records, rec)
		}
		n, err := r.Store.IndexMovies(ctx, records, IndexMoviesOptions{
			IncludeWords:  opts.IncludeWords,
			MinWordLength: opts.MinWordLength,
			BatchSize:     opts.BatchSize,
		})
		if err != nil {
			return st, err
		}
		st.MoviesIndexed = n
	}

	if opts.IncludeActors {
		actors, err := r.fetchActors(ctx, opts.ActorsLimit, opts.MaxPages, opts.RequestTimeout)
		if err != nil {
			return st, err
		}
		st.ActorsFetched = len(actors)

		records := make([]ActorRecord, 0, len(actors))
		for _, a := range actors {
			rec, ok := mapActor(a)
			if !ok {
				continue
			}
			records = append(records, rec)
		}
		n, err := r.Store.IndexActors(ctx, records, IndexActorsOptions{BatchSize: opts.BatchSize})
		if err != nil {
			return st, err
		}
		st.ActorsIndexed = n
	}

	return st, nil
}

func (r *Runner) fetchMovies(ctx context.Context, limit, maxPages int, reqTimeout time.Duration) ([]backend.Movie, error) {
	pageSize := 100
	if limit > 0 && limit < pageSize {
		pageSize = limit
	}

	var out []backend.Movie
	for page := 1; page <= maxPages; page++ {
		if limit > 0 && len(out) >= limit {
			break
		}
		currentSize := pageSize
		if limit > 0 {
			remaining := limit - len(out)
			if remaining < currentSize {
				currentSize = remaining
			}
		}

		reqCtx, cancel := withTimeout(ctx, reqTimeout)
		resp, err := r.Backend.ListMovies(reqCtx, page, currentSize, "imdb_rating", true)
		cancel()
		if err != nil {
			return nil, err
		}
		if len(resp.Results) == 0 {
			break
		}
		out = append(out, resp.Results...)
		if !resp.HasNext {
			break
		}
	}
	return out, nil
}

func (r *Runner) fetchActors(ctx context.Context, limit, maxPages int, reqTimeout time.Duration) ([]backend.Actor, error) {
	pageSize := 100
	if limit > 0 && limit < pageSize {
		pageSize = limit
	}

	var out []backend.Actor
	for page := 1; page <= maxPages; page++ {
		if limit > 0 && len(out) >= limit {
			break
		}
		currentSize := pageSize
		if limit > 0 {
			remaining := limit - len(out)
			if remaining < currentSize {
				currentSize = remaining
			}
		}

		reqCtx, cancel := withTimeout(ctx, reqTimeout)
		resp, err := r.Backend.ListActors(reqCtx, page, currentSize)
		cancel()
		if err != nil {
			return nil, err
		}
		if len(resp.Actors) == 0 {
			break
		}
		out = append(out, resp.Actors...)
		// Backend actors response doesn't include has_next; infer via page sizing.
		if len(resp.Actors) < currentSize {
			break
		}
	}
	return out, nil
}

func mapMovie(m backend.Movie) (MovieRecord, bool) {
	if m.ID <= 0 {
		return MovieRecord{}, false
	}
	title := strings.TrimSpace(m.Title)
	if title == "" {
		return MovieRecord{}, false
	}

	var year *int
	if m.ReleaseDate != nil {
		// backend sends YYYY-MM-DD as string; take first 4.
		if len(*m.ReleaseDate) >= 4 {
			if y, err := strconv.Atoi((*m.ReleaseDate)[:4]); err == nil && y > 0 {
				year = &y
			}
		}
	}

	return MovieRecord{
		ID:                  m.ID,
		Title:               title,
		Type:                "movie",
		ImagePath:           m.PosterURL,
		Year:                year,
		Popularity:          m.Popularity,
		VoteAverage:         m.VoteAverage,
		OriginalTitleFormat: title,

		Overview:    m.Overview,
		ReleaseDate: m.ReleaseDate,
		BackdropURL: m.BackdropURL,
		IMDBRating:  m.IMDBRating,
		Runtime:     m.Runtime,
		Genres:      m.Genres,
		TMDBID:      m.TMDBID,
		IMDBID:      m.IMDBID,
	}, true
}

func mapActor(a backend.Actor) (ActorRecord, bool) {
	if a.ID <= 0 {
		return ActorRecord{}, false
	}
	name := strings.TrimSpace(a.Name)
	if name == "" {
		return ActorRecord{}, false
	}
	return ActorRecord{
		ID:         a.ID,
		Name:       name,
		Type:       "actor",
		ImagePath:  a.ProfilePath,
		Popularity: a.Popularity,
	}, true
}

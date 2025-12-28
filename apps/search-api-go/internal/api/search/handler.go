package search

import (
	"context"
	"encoding/json"
	"math"
	"net/http"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog/log"

	"github.com/next-watch/search-api-go/internal/indexer"
)

type Handler struct {
	Store *indexer.RedisV2Store
}

func (h Handler) Routes(r chi.Router) {
	r.Get("/search/suggestions", h.getSuggestions)
	r.Get("/search/suggestions/text", h.getTextSuggestions)
	r.Get("/search/all", h.searchAll)
	r.Get("/search", h.searchMovies)
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func writeError(w http.ResponseWriter, status int, detail string) {
	writeJSON(w, status, map[string]any{"detail": detail})
}

func parseInt(q urlValues, key string, def, min, max int) int {
	raw := strings.TrimSpace(q.Get(key))
	if raw == "" {
		return def
	}
	n, err := strconv.Atoi(raw)
	if err != nil {
		return def
	}
	if n < min {
		return min
	}
	if n > max {
		return max
	}
	return n
}

// urlValues is the subset we need from url.Values.
type urlValues interface {
	Get(key string) string
}

type candidate struct {
	EntityType string // movie|actor
	Text       string // normalized key text
	Display    string
	Movie      *indexer.MovieRecord
	Actor      *indexer.ActorRecord
	Exact      bool
	Popularity float64
}

func (c candidate) id() int {
	if c.Movie != nil {
		return c.Movie.ID
	}
	if c.Actor != nil {
		return c.Actor.ID
	}
	return 0
}

func normalize(s string) string {
	return strings.ToLower(strings.TrimSpace(s))
}

func (h Handler) fetchCandidates(ctx context.Context, query string, limit int, types []string) ([]candidate, error) {
	if h.Store == nil {
		return nil, nil
	}
	q := normalize(query)
	if q == "" || limit <= 0 {
		return []candidate{}, nil
	}

	// Default types if none provided.
	if len(types) == 0 {
		types = []string{"movie", "actor"}
	}

	// Fetch a bit more per type so merge + dedupe doesn't starve the output.
	perTypeLimit := int64(limit * 2)
	if perTypeLimit < 10 {
		perTypeLimit = 10
	}

	var out []candidate
	seen := make(map[string]struct{}, limit*2)

	for _, t := range types {
		t = strings.TrimSpace(strings.ToLower(t))
		if t != "movie" && t != "actor" {
			continue
		}

		texts, err := h.Store.PrefixEntityTexts(ctx, t, q, perTypeLimit)
		if err != nil {
			return nil, err
		}
		if len(texts) == 0 {
			continue
		}

		switch t {
		case "movie":
			recs, err := h.Store.LoadMoviesByText(ctx, texts)
			if err != nil {
				return nil, err
			}
			for _, text := range texts {
				rec, ok := recs[normalize(text)]
				if !ok || rec.ID <= 0 {
					continue
				}
				key := "movie:" + strconv.Itoa(rec.ID)
				if _, ok := seen[key]; ok {
					continue
				}
				seen[key] = struct{}{}
				pop := 0.0
				if rec.Popularity != nil {
					pop = *rec.Popularity
				}
				out = append(out, candidate{
					EntityType: "movie",
					Text:       normalize(text),
					Display:    rec.Title,
					Movie:      &rec,
					Exact:      normalize(text) == q,
					Popularity: pop,
				})
			}
		case "actor":
			recs, err := h.Store.LoadActorsByText(ctx, texts)
			if err != nil {
				return nil, err
			}
			for _, text := range texts {
				rec, ok := recs[normalize(text)]
				if !ok || rec.ID <= 0 {
					continue
				}
				key := "actor:" + strconv.Itoa(rec.ID)
				if _, ok := seen[key]; ok {
					continue
				}
				seen[key] = struct{}{}
				pop := 0.0
				if rec.Popularity != nil {
					pop = *rec.Popularity
				}
				out = append(out, candidate{
					EntityType: "actor",
					Text:       normalize(text),
					Display:    rec.Name,
					Actor:      &rec,
					Exact:      normalize(text) == q,
					Popularity: pop,
				})
			}
		}
	}

	sort.Slice(out, func(i, j int) bool {
		// Exact matches first.
		if out[i].Exact != out[j].Exact {
			return out[i].Exact
		}
		// Higher popularity first.
		if out[i].Popularity != out[j].Popularity {
			return out[i].Popularity > out[j].Popularity
		}
		// Stable-ish alphabetical tie-break.
		return strings.ToLower(out[i].Display) < strings.ToLower(out[j].Display)
	})

	if len(out) > limit {
		out = out[:limit]
	}
	return out, nil
}

func searchMetadata(total int, searchType, suggestionType string) map[string]any {
	md := map[string]any{
		"total": total,
		"service_info": map[string]any{
			"service_name":   "search-api",
			"search_backend": "redis",
		},
		"api_version":      "v1",
		"response_pattern": "search",
		"search_context":   map[string]any{"search_type": searchType},
	}
	if suggestionType != "" {
		md["search_context"] = map[string]any{
			"search_type":     searchType,
			"suggestion_type": suggestionType,
		}
	}
	return md
}

func paginatedMetadata(query string, searchType string, types []string) map[string]any {
	return map[string]any{
		"query": query,
		"filters_applied": map[string]any{
			"types": types,
		},
		"service_info": map[string]any{
			"service_name":   "search-api",
			"search_backend": "redis",
		},
		"api_version":      "v1",
		"response_pattern": "paginated",
		"search_context": map[string]any{
			"search_type":  searchType,
			"entity_types": types,
		},
	}
}

func (h Handler) withRedisTimeout(r *http.Request) (context.Context, context.CancelFunc) {
	return context.WithTimeout(r.Context(), 750*time.Millisecond)
}

func (h Handler) getSuggestions(w http.ResponseWriter, r *http.Request) {
	if h.Store == nil {
		writeError(w, http.StatusServiceUnavailable, "Redis not configured")
		return
	}
	qp := r.URL.Query()
	query := strings.TrimSpace(qp.Get("query"))
	if query == "" {
		writeError(w, http.StatusBadRequest, "Search query cannot be empty")
		return
	}
	limit := parseInt(qp, "limit", 10, 1, 50)

	ctx, cancel := h.withRedisTimeout(r)
	defer cancel()

	cands, err := h.fetchCandidates(ctx, query, limit, nil)
	if err != nil {
		log.Error().Err(err).Msg("getSuggestions failed")
		writeError(w, http.StatusInternalServerError, "Internal server error")
		return
	}

	results := make([]map[string]any, 0, len(cands))
	for _, c := range cands {
		if c.Movie != nil {
			results = append(results, map[string]any{
				"id":         c.Movie.ID,
				"name":       c.Movie.Title,
				"type":       "movie",
				"image_path": c.Movie.ImagePath,
			})
		} else if c.Actor != nil {
			results = append(results, map[string]any{
				"id":         c.Actor.ID,
				"name":       c.Actor.Name,
				"type":       "actor",
				"image_path": c.Actor.ImagePath,
			})
		}
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"query":    query,
		"results":  results,
		"metadata": searchMetadata(len(results), "suggestions", "basic"),
	})
}

func (h Handler) getTextSuggestions(w http.ResponseWriter, r *http.Request) {
	if h.Store == nil {
		writeError(w, http.StatusServiceUnavailable, "Redis not configured")
		return
	}
	qp := r.URL.Query()
	query := strings.TrimSpace(qp.Get("query"))
	if query == "" {
		writeError(w, http.StatusBadRequest, "Search query cannot be empty")
		return
	}
	limit := parseInt(qp, "limit", 10, 1, 50)

	ctx, cancel := h.withRedisTimeout(r)
	defer cancel()

	cands, err := h.fetchCandidates(ctx, query, limit, nil)
	if err != nil {
		log.Error().Err(err).Msg("getTextSuggestions failed")
		writeError(w, http.StatusInternalServerError, "Internal server error")
		return
	}

	qn := normalize(query)
	results := make([]map[string]any, 0, len(cands))
	for _, c := range cands {
		searchType := "prefix"
		if c.Exact {
			searchType = "exact"
		}
		isPartial := !c.Exact && qn != ""

		if c.Movie != nil {
			additional := map[string]any{
				"vote_average": c.Movie.VoteAverage,
				"overview":     c.Movie.Overview,
				"genres":       c.Movie.Genres,
				"imdb_rating":  c.Movie.IMDBRating,
				"runtime":      c.Movie.Runtime,
			}
			results = append(results, map[string]any{
				"text":            c.Movie.Title,
				"type":            "movie",
				"id":              c.Movie.ID,
				"image_path":      c.Movie.ImagePath,
				"year":            c.Movie.Year,
				"popularity":      c.Movie.Popularity,
				"is_partial":      isPartial,
				"search_type":     searchType,
				"additional_info": additional,
			})
		} else if c.Actor != nil {
			results = append(results, map[string]any{
				"text":            c.Actor.Name,
				"type":            "actor",
				"id":              c.Actor.ID,
				"image_path":      c.Actor.ImagePath,
				"popularity":      c.Actor.Popularity,
				"is_partial":      isPartial,
				"search_type":     searchType,
				"additional_info": map[string]any{},
			})
		}
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"query":    query,
		"results":  results,
		"metadata": searchMetadata(len(results), "suggestions", "text"),
	})
}

func (h Handler) searchAll(w http.ResponseWriter, r *http.Request) {
	if h.Store == nil {
		writeError(w, http.StatusServiceUnavailable, "Redis not configured")
		return
	}
	qp := r.URL.Query()
	query := strings.TrimSpace(qp.Get("query"))
	if query == "" {
		writeError(w, http.StatusBadRequest, "Search query cannot be empty")
		return
	}

	page := parseInt(qp, "page", 1, 1, 1000000)
	limit := parseInt(qp, "limit", 20, 1, 100)

	types := qp["types"]
	if len(types) == 0 {
		// Support comma-separated types=movie,actor
		if raw := strings.TrimSpace(qp.Get("types")); raw != "" {
			parts := strings.Split(raw, ",")
			for _, p := range parts {
				p = strings.TrimSpace(p)
				if p != "" {
					types = append(types, p)
				}
			}
		}
	}

	// Fetch a bounded candidate pool to approximate "total" like the Python service does.
	fetchLimit := page * limit * 5
	if fetchLimit < 50 {
		fetchLimit = 50
	}
	if fetchLimit > 1000 {
		fetchLimit = 1000
	}

	ctx, cancel := h.withRedisTimeout(r)
	defer cancel()

	cands, err := h.fetchCandidates(ctx, query, fetchLimit, types)
	if err != nil {
		log.Error().Err(err).Msg("searchAll failed")
		writeError(w, http.StatusInternalServerError, "Internal server error")
		return
	}

	total := len(cands)
	totalPages := 0
	if limit > 0 {
		totalPages = int(math.Ceil(float64(total) / float64(limit)))
	}
	hasNext := page < totalPages
	hasPrev := page > 1

	start := (page - 1) * limit
	end := start + limit
	if start > total {
		start = total
	}
	if end > total {
		end = total
	}
	pageCands := cands[start:end]

	results := make([]map[string]any, 0, len(pageCands))
	for _, c := range pageCands {
		if c.Movie != nil {
			results = append(results, map[string]any{
				"id":              c.Movie.ID,
				"name":            c.Movie.Title,
				"type":            "movie",
				"image_path":      c.Movie.ImagePath,
				"year":            c.Movie.Year,
				"popularity":      c.Movie.Popularity,
				"additional_info": map[string]any{},
			})
		} else if c.Actor != nil {
			results = append(results, map[string]any{
				"id":              c.Actor.ID,
				"name":            c.Actor.Name,
				"type":            "actor",
				"image_path":      c.Actor.ImagePath,
				"popularity":      c.Actor.Popularity,
				"additional_info": map[string]any{},
			})
		}
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"results": results,
		"pagination": map[string]any{
			"page":        page,
			"per_page":    limit,
			"total":       total,
			"total_pages": totalPages,
			"has_next":    hasNext,
			"has_prev":    hasPrev,
		},
		"metadata": paginatedMetadata(query, "all_entities", types),
	})
}

func (h Handler) searchMovies(w http.ResponseWriter, r *http.Request) {
	if h.Store == nil {
		writeError(w, http.StatusServiceUnavailable, "Redis not configured")
		return
	}
	qp := r.URL.Query()
	query := strings.TrimSpace(qp.Get("q"))
	if query == "" {
		// Support query= as well for consistency with other endpoints.
		query = strings.TrimSpace(qp.Get("query"))
	}
	if query == "" {
		writeError(w, http.StatusBadRequest, "Search query cannot be empty")
		return
	}

	page := parseInt(qp, "page", 1, 1, 1000000)
	limit := parseInt(qp, "limit", 20, 1, 100)

	fetchLimit := page * limit * 5
	if fetchLimit < 50 {
		fetchLimit = 50
	}
	if fetchLimit > 1000 {
		fetchLimit = 1000
	}

	ctx, cancel := h.withRedisTimeout(r)
	defer cancel()

	cands, err := h.fetchCandidates(ctx, query, fetchLimit, []string{"movie"})
	if err != nil {
		log.Error().Err(err).Msg("searchMovies failed")
		writeError(w, http.StatusInternalServerError, "Internal server error")
		return
	}

	total := len(cands)
	totalPages := 0
	if limit > 0 {
		totalPages = int(math.Ceil(float64(total) / float64(limit)))
	}
	hasNext := page < totalPages
	hasPrev := page > 1

	start := (page - 1) * limit
	end := start + limit
	if start > total {
		start = total
	}
	if end > total {
		end = total
	}
	pageCands := cands[start:end]

	results := make([]map[string]any, 0, len(pageCands))
	for _, c := range pageCands {
		if c.Movie == nil {
			continue
		}
		// Mirror the Python SearchService movie mapping.
		releaseYear := any(nil)
		if c.Movie.Year != nil {
			releaseYear = *c.Movie.Year
		}
		results = append(results, map[string]any{
			"id":           c.Movie.ID,
			"title":        c.Movie.Title,
			"release_year": releaseYear,
			"poster_url":   c.Movie.ImagePath,
			"vote_average": c.Movie.VoteAverage,
			"popularity":   c.Movie.Popularity,
			"overview":     c.Movie.Overview,
			"genres":       c.Movie.Genres,
			"imdb_rating":  c.Movie.IMDBRating,
			"runtime":      c.Movie.Runtime,
		})
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"results": results,
		"pagination": map[string]any{
			"page":        page,
			"per_page":    limit,
			"total":       total,
			"total_pages": totalPages,
			"has_next":    hasNext,
			"has_prev":    hasPrev,
		},
		"metadata": map[string]any{
			"query": query,
			"service_info": map[string]any{
				"service_name":   "search-api",
				"search_backend": "redis",
			},
			"api_version":      "v1",
			"response_pattern": "paginated",
			"search_context": map[string]any{
				"search_type": "movies",
			},
		},
	})
}

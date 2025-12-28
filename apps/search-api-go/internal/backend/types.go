package backend

// Movie is a subset of Backend API's movie payload used by search indexing.
// We intentionally keep fields permissive (pointers) to tolerate backend changes.
type Movie struct {
	ID          int      `json:"id"`
	Title       string   `json:"title"`
	Overview    *string  `json:"overview,omitempty"`
	ReleaseDate *string  `json:"release_date,omitempty"`
	PosterURL   *string  `json:"poster_url,omitempty"`
	BackdropURL *string  `json:"backdrop_url,omitempty"`
	Popularity  *float64 `json:"popularity,omitempty"`
	VoteAverage *float64 `json:"vote_average,omitempty"`
	IMDBRating  *float64 `json:"imdb_rating,omitempty"`
	Runtime     *int     `json:"runtime,omitempty"`
	Genres      []any    `json:"genres,omitempty"`
	TMDBID      *int     `json:"tmdb_id,omitempty"`
	IMDBID      *string  `json:"imdb_id,omitempty"`
}

type MoviesListResponse struct {
	Total      int    `json:"total"`
	Page       int    `json:"page"`
	PerPage    int    `json:"per_page"`
	TotalPages int    `json:"total_pages"`
	HasNext    bool   `json:"has_next"`
	HasPrev    bool   `json:"has_prev"`
	Results    []Movie `json:"results"`
}

// Actor is a subset of Backend API's actor payload used by search indexing.
type Actor struct {
	ID          int      `json:"id"`
	Name        string   `json:"name"`
	ProfilePath *string  `json:"profile_path,omitempty"`
	Popularity  *float64 `json:"popularity,omitempty"`
}

type ActorsListResponse struct {
	Actors []Actor `json:"actors"`
	Total  int     `json:"total"`
}

package indexer

// These records are stored in Redis v2 as JSON blobs.

type MovieRecord struct {
	ID                  int      `json:"id"`
	Title               string   `json:"title"`
	Type                string   `json:"type"`
	ImagePath           *string  `json:"image_path,omitempty"`
	Year                *int     `json:"year,omitempty"`
	Popularity          *float64 `json:"popularity,omitempty"`
	VoteAverage         *float64 `json:"vote_average,omitempty"`
	OriginalTitleFormat string   `json:"original_title_format"`

	Overview     *string `json:"overview,omitempty"`
	ReleaseDate  *string `json:"release_date,omitempty"`
	BackdropURL  *string `json:"backdrop_url,omitempty"`
	IMDBRating   *float64 `json:"imdb_rating,omitempty"`
	Runtime      *int     `json:"runtime,omitempty"`
	Genres       []any    `json:"genres,omitempty"`
	TMDBID       *int     `json:"tmdb_id,omitempty"`
	IMDBID       *string  `json:"imdb_id,omitempty"`
}

type ActorRecord struct {
	ID        int      `json:"id"`
	Name      string   `json:"name"`
	Type      string   `json:"type"`
	ImagePath *string  `json:"image_path,omitempty"`
	Popularity *float64 `json:"popularity,omitempty"`
}

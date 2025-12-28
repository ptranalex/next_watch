package redisv2

import "context"

// Reader is the runtime read-path for Redis v2.
//
// Indexing is handled separately (see internal/indexer/redis_v2_store.go).
type Reader interface {
	// PrefixMatches returns normalized suggestion texts matching the given prefix for a single entity type.
	PrefixMatches(ctx context.Context, t EntityType, queryPrefix string, limit int64) ([]string, error)

	// SubstringMatches returns (type,text) refs whose text contains the given query substring.
	// Results are bounded by time/page limits in the implementation.
	SubstringMatches(ctx context.Context, types []EntityType, query string, limit int) ([]SuggestionRef, error)

	// Hydrate fetches entity JSON blobs for refs.
	Hydrate(ctx context.Context, refs []SuggestionRef) ([]HydratedEntity, error)
}

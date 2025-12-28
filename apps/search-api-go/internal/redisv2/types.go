package redisv2

import "encoding/json"

// EntityType is a logical search entity namespace (e.g. "movie", "actor").
type EntityType string

const (
	EntityTypeMovie    EntityType = "movie"
	EntityTypeActor    EntityType = "actor"
	EntityTypeDirector EntityType = "director"
)

// SuggestionRef is a reference to an entity stored in Redis v2 by (type, normalized text).
type SuggestionRef struct {
	Type EntityType
	Text string // normalized, as stored in the ZSET / entity key
}

// HydratedEntity is the hydrated entity payload as stored in Redis (JSON blob).
// Callers can decode Raw into a typed struct if desired.
type HydratedEntity struct {
	Ref SuggestionRef
	Raw json.RawMessage
}

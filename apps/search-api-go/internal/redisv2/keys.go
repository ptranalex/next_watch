package redisv2

import (
	"strconv"
	"strings"
)

// Keyspace helpers for Redis schema v2.
//
// Base prefix is "search:v2" by default (no trailing ':').

func cleanPrefix(prefix string) string {
	prefix = strings.TrimSpace(prefix)
	prefix = strings.TrimSuffix(prefix, ":")
	if prefix == "" {
		return "search:v2"
	}
	return prefix
}

func suggestionsKey(prefix string, t EntityType) string {
	return cleanPrefix(prefix) + ":suggestions:" + string(t)
}

func entityKey(prefix string, t EntityType, text string) string {
	return cleanPrefix(prefix) + ":entity:" + string(t) + ":" + text
}

func entityByIDKey(prefix string, t EntityType, id int) string {
	return cleanPrefix(prefix) + ":entity_by_id:" + string(t) + ":" + strconv.Itoa(id)
}

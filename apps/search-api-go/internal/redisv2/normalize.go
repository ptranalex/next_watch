package redisv2

import "strings"

// NormalizeQuery matches the Python Search API behavior (lower + trim).
func NormalizeQuery(s string) string {
	return strings.ToLower(strings.TrimSpace(s))
}

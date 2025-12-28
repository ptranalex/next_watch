package redisv2

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

type Store struct {
	prefix string
	rc     *redis.Client

	// Substring matching controls (used by SubstringMatches).
	substrMinLen    int
	substrBudget    time.Duration
	substrPageLimit int
	zscanCount      int64
}

type Options struct {
	RedisURL string
	// Prefix like "search:v2" (no trailing ':'). If empty, defaults to "search:v2".
	Prefix string

	// SubstringMinLength: minimum query length to enable substring matching (default 3).
	SubstringMinLength int
	// SubstringTimeBudget: wall-clock budget for substring matching across all types (default 80ms).
	SubstringTimeBudget time.Duration
	// SubstringScanPageLimit: max ZSCAN pages per entity type (default 5).
	SubstringScanPageLimit int
	// ZScanCount: Redis ZSCAN COUNT (default 200).
	ZScanCount int64
}

func New(opts Options) (*Store, error) {
	if strings.TrimSpace(opts.RedisURL) == "" {
		return nil, fmt.Errorf("redis url is required")
	}
	redisOpts, err := redis.ParseURL(opts.RedisURL)
	if err != nil {
		return nil, err
	}

	minLen := opts.SubstringMinLength
	if minLen <= 0 {
		minLen = 3
	}
	budget := opts.SubstringTimeBudget
	if budget <= 0 {
		budget = 80 * time.Millisecond
	}
	pageLimit := opts.SubstringScanPageLimit
	if pageLimit <= 0 {
		pageLimit = 5
	}
	count := opts.ZScanCount
	if count <= 0 {
		count = 200
	}

	return &Store{
		prefix:          cleanPrefix(opts.Prefix),
		rc:              redis.NewClient(redisOpts),
		substrMinLen:    minLen,
		substrBudget:    budget,
		substrPageLimit: pageLimit,
		zscanCount:      count,
	}, nil
}

func (s *Store) Close() error {
	if s == nil || s.rc == nil {
		return nil
	}
	return s.rc.Close()
}

func (s *Store) Ping(ctx context.Context) error {
	if s == nil || s.rc == nil {
		return redis.ErrClosed
	}
	_, err := s.rc.Ping(ctx).Result()
	return err
}

// PrefixMatches returns normalized suggestion texts matching the given prefix for a single entity type.
// Uses lexicographical range on the per-type ZSET: "<prefix>:suggestions:<type>".
func (s *Store) PrefixMatches(ctx context.Context, t EntityType, queryPrefix string, limit int64) ([]string, error) {
	if limit <= 0 {
		return []string{}, nil
	}
	q := NormalizeQuery(queryPrefix)
	if q == "" {
		return []string{}, nil
	}

	// Mirror Python behavior: min="["+q, max="["+q+"\xff"
	min := "[" + q
	max := "[" + q + "\xff"
	key := suggestionsKey(s.prefix, t)

	res, err := s.rc.ZRangeByLex(ctx, key, &redis.ZRangeBy{
		Min:    min,
		Max:    max,
		Offset: 0,
		Count:  limit,
	}).Result()
	if err != nil {
		return nil, err
	}
	return res, nil
}

// SubstringMatches returns normalized suggestion texts containing query as a substring.
//
// This is intentionally bounded:
// - disabled for very short queries (min length)
// - time-budgeted
// - page-limited per type
//
// Implementation uses ZSCAN MATCH "*<query>*" against the per-type ZSET, which bounds the scan
// to the suggestion index instead of scanning arbitrary Redis keys.
func (s *Store) SubstringMatches(ctx context.Context, types []EntityType, query string, limit int) ([]SuggestionRef, error) {
	if limit <= 0 {
		return []SuggestionRef{}, nil
	}
	q := NormalizeQuery(query)
	if q == "" {
		return []SuggestionRef{}, nil
	}
	if len(q) < s.substrMinLen {
		return []SuggestionRef{}, nil
	}
	if len(types) == 0 {
		return []SuggestionRef{}, nil
	}

	deadline := time.Now().Add(s.substrBudget)
	match := "*" + q + "*"

	out := make([]SuggestionRef, 0, limit)
	seen := make(map[string]struct{}, limit*2) // key = type+"\x00"+text

	add := func(t EntityType, text string) bool {
		if text == "" {
			return false
		}
		k := string(t) + "\x00" + text
		if _, ok := seen[k]; ok {
			return false
		}
		seen[k] = struct{}{}
		out = append(out, SuggestionRef{Type: t, Text: text})
		return true
	}

	for _, t := range types {
		if time.Now().After(deadline) {
			break
		}
		key := suggestionsKey(s.prefix, t)

		var cursor uint64
		pages := 0
		for {
			if len(out) >= limit {
				return out[:limit], nil
			}
			if pages >= s.substrPageLimit {
				break
			}
			if time.Now().After(deadline) {
				break
			}

			// go-redis returns a slice alternating member, score, member, score...
			page, next, err := s.rc.ZScan(ctx, key, cursor, match, s.zscanCount).Result()
			if err != nil {
				return nil, err
			}
			pages++

			for i := 0; i < len(page); i += 2 {
				if len(out) >= limit {
					return out[:limit], nil
				}
				member := page[i]
				// Member is already normalized during indexing; normalize defensively.
				member = NormalizeQuery(member)
				if member == "" {
					continue
				}
				add(t, member)
			}

			cursor = next
			if cursor == 0 {
				break
			}
		}
	}

	if len(out) > limit {
		out = out[:limit]
	}
	return out, nil
}

// Hydrate fetches entity JSON blobs for (type, text) refs in a single round-trip per entity type.
// It returns only refs that were successfully found+decoded.
func (s *Store) Hydrate(ctx context.Context, refs []SuggestionRef) ([]HydratedEntity, error) {
	if len(refs) == 0 {
		return []HydratedEntity{}, nil
	}

	// Group by type; hydrate by text.
	type group struct {
		refs []SuggestionRef
		keys []string
	}
	groups := make(map[EntityType]*group, 4)
	for _, r := range refs {
		t := r.Type
		if t == "" {
			continue
		}
		text := NormalizeQuery(r.Text)
		if text == "" {
			continue
		}
		r.Text = text

		g := groups[t]
		if g == nil {
			g = &group{}
			groups[t] = g
		}
		g.refs = append(g.refs, r)
		g.keys = append(g.keys, entityKey(s.prefix, t, text))
	}

	out := make([]HydratedEntity, 0, len(refs))
	for t, g := range groups {
		vals, err := s.rc.MGet(ctx, g.keys...).Result()
		if err != nil {
			return nil, err
		}
		for i := range vals {
			if vals[i] == nil {
				continue
			}

			var raw []byte
			switch v := vals[i].(type) {
			case string:
				raw = []byte(v)
			case []byte:
				raw = v
			default:
				// go-redis may return other scalar types; stringify.
				raw = []byte(fmt.Sprint(v))
			}

			// Validate JSON (so callers don't have to).
			var tmp any
			if err := json.Unmarshal(raw, &tmp); err != nil {
				continue
			}

			out = append(out, HydratedEntity{
				Ref: SuggestionRef{Type: t, Text: g.refs[i].Text},
				Raw: json.RawMessage(raw),
			})
		}
	}

	return out, nil
}

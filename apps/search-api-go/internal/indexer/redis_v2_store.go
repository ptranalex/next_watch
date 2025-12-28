package indexer

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisV2Store struct {
	prefix string
	rc     *redis.Client
}

type RedisV2StoreOptions struct {
	RedisURL string
	// Prefix like "search:v2" (no trailing ':').
	Prefix string
}

func NewRedisV2Store(opts RedisV2StoreOptions) (*RedisV2Store, error) {
	if strings.TrimSpace(opts.RedisURL) == "" {
		return nil, fmt.Errorf("redis url is required")
	}
	prefix := strings.TrimSpace(opts.Prefix)
	prefix = strings.TrimSuffix(prefix, ":")
	if prefix == "" {
		prefix = "search:v2"
	}

	redisOpts, err := redis.ParseURL(opts.RedisURL)
	if err != nil {
		return nil, err
	}

	return &RedisV2Store{
		prefix: prefix,
		rc:     redis.NewClient(redisOpts),
	}, nil
}

func (s *RedisV2Store) Close() error {
	if s == nil || s.rc == nil {
		return nil
	}
	return s.rc.Close()
}

func (s *RedisV2Store) Ping(ctx context.Context) error {
	if s == nil || s.rc == nil {
		return redis.ErrClosed
	}
	_, err := s.rc.Ping(ctx).Result()
	return err
}

func (s *RedisV2Store) ClearPrefix(ctx context.Context, batchSize int64) (int64, error) {
	if batchSize <= 0 {
		batchSize = 1000
	}
	var deleted int64
	var cursor uint64
	match := s.prefix + ":*"

	for {
		var keys []string
		var err error
		keys, cursor, err = s.rc.Scan(ctx, cursor, match, batchSize).Result()
		if err != nil {
			return deleted, err
		}
		if len(keys) > 0 {
			n, err := s.rc.Del(ctx, keys...).Result()
			if err != nil {
				return deleted, err
			}
			deleted += n
		}
		if cursor == 0 {
			break
		}
	}
	return deleted, nil
}

type IndexMoviesOptions struct {
	IncludeWords  bool
	MinWordLength int
	BatchSize     int
}

func (s *RedisV2Store) IndexMovies(ctx context.Context, movies []MovieRecord, opts IndexMoviesOptions) (int, error) {
	if opts.BatchSize <= 0 {
		opts.BatchSize = 100
	}
	if opts.MinWordLength <= 0 {
		opts.MinWordLength = 3
	}

	zsetKey := s.prefix + ":suggestions:movie"
	byIDPrefix := s.prefix + ":entity_by_id:movie:"
	entityPrefix := s.prefix + ":entity:movie:"

	pipe := s.rc.Pipeline()
	queued := 0

	flush := func() error {
		if queued == 0 {
			return nil
		}
		_, err := pipe.Exec(ctx)
		pipe = s.rc.Pipeline()
		queued = 0
		return err
	}

	for i := range movies {
		m := movies[i]
		if m.ID <= 0 || strings.TrimSpace(m.Title) == "" {
			continue
		}

		// Store by-id record once.
		rawByID, err := json.Marshal(m)
		if err != nil {
			return 0, err
		}
		pipe.Set(ctx, byIDPrefix+strconv.Itoa(m.ID), rawByID, 0)
		queued++

		vars := movieVariations(m.Title, opts.IncludeWords, opts.MinWordLength)
		for _, v := range vars {
			// ZSET member for lex search.
			pipe.ZAdd(ctx, zsetKey, redis.Z{Score: 0, Member: v})
			queued++

			// Canonical payload keyed by the searchable text.
			// This duplicates JSON per variation, but keeps the runtime read path simple.
			pipe.Set(ctx, entityPrefix+v, rawByID, 0)
			queued++
		}

		if (i+1)%opts.BatchSize == 0 {
			if err := flush(); err != nil {
				return 0, err
			}
		}
	}

	if err := flush(); err != nil {
		return 0, err
	}

	return len(movies), nil
}

type IndexActorsOptions struct {
	BatchSize int
}

func (s *RedisV2Store) IndexActors(ctx context.Context, actors []ActorRecord, opts IndexActorsOptions) (int, error) {
	if opts.BatchSize <= 0 {
		opts.BatchSize = 100
	}

	zsetKey := s.prefix + ":suggestions:actor"
	byIDPrefix := s.prefix + ":entity_by_id:actor:"
	entityPrefix := s.prefix + ":entity:actor:"

	pipe := s.rc.Pipeline()
	queued := 0

	flush := func() error {
		if queued == 0 {
			return nil
		}
		_, err := pipe.Exec(ctx)
		pipe = s.rc.Pipeline()
		queued = 0
		return err
	}

	for i := range actors {
		a := actors[i]
		if a.ID <= 0 || strings.TrimSpace(a.Name) == "" {
			continue
		}

		raw, err := json.Marshal(a)
		if err != nil {
			return 0, err
		}

		n := normalizeText(a.Name)
		if n == "" {
			continue
		}

		pipe.Set(ctx, byIDPrefix+strconv.Itoa(a.ID), raw, 0)
		queued++
		pipe.ZAdd(ctx, zsetKey, redis.Z{Score: 0, Member: n})
		queued++
		pipe.Set(ctx, entityPrefix+n, raw, 0)
		queued++

		if (i+1)%opts.BatchSize == 0 {
			if err := flush(); err != nil {
				return 0, err
			}
		}
	}

	if err := flush(); err != nil {
		return 0, err
	}

	return len(actors), nil
}

type Counts struct {
	MovieSuggestions int64
	ActorSuggestions int64
	Entities         int64
}

func (s *RedisV2Store) Counts(ctx context.Context) (Counts, error) {
	var out Counts

	movieZ := s.prefix + ":suggestions:movie"
	actorZ := s.prefix + ":suggestions:actor"

	mc, err := s.rc.ZCard(ctx, movieZ).Result()
	if err != nil {
		return Counts{}, err
	}
	ac, err := s.rc.ZCard(ctx, actorZ).Result()
	if err != nil {
		return Counts{}, err
	}
	out.MovieSuggestions = mc
	out.ActorSuggestions = ac

	// Count entity keys via SCAN; bounded to prefix.
	var cursor uint64
	var total int64
	for {
		keys, next, err := s.rc.Scan(ctx, cursor, s.prefix+":entity:*", 1000).Result()
		if err != nil {
			return Counts{}, err
		}
		total += int64(len(keys))
		cursor = next
		if cursor == 0 {
			break
		}
	}
	out.Entities = total
	return out, nil
}

// PrefixEntityTexts returns normalized entity texts matching the given prefix for an entity type.
// It uses ZRANGEBYLEX on the v2 ZSET (member=normalized text, score=0).
func (s *RedisV2Store) PrefixEntityTexts(ctx context.Context, entityType, query string, limit int64) ([]string, error) {
	if s == nil || s.rc == nil {
		return nil, redis.ErrClosed
	}
	entityType = strings.TrimSpace(strings.ToLower(entityType))
	if entityType == "" {
		return nil, fmt.Errorf("entity type is required")
	}
	q := normalizeText(query)
	if q == "" || limit <= 0 {
		return []string{}, nil
	}

	zsetKey := s.prefix + ":suggestions:" + entityType
	// Prefix lex range: [q, [q\xff
	min := "[" + q
	max := "[" + q + "\xff"
	return s.rc.ZRangeByLex(ctx, zsetKey, &redis.ZRangeBy{
		Min:    min,
		Max:    max,
		Offset: 0,
		Count:  limit,
	}).Result()
}

func (s *RedisV2Store) getJSONByKeys(ctx context.Context, keys []string) (map[string]string, error) {
	if len(keys) == 0 {
		return map[string]string{}, nil
	}
	pipe := s.rc.Pipeline()
	cmds := make([]*redis.StringCmd, 0, len(keys))
	for _, k := range keys {
		cmds = append(cmds, pipe.Get(ctx, k))
	}
	_, err := pipe.Exec(ctx)
	if err != nil && err != redis.Nil {
		// Note: go-redis may return redis.Nil if some keys are missing; we ignore those below.
		// Other errors are fatal.
		return nil, err
	}

	out := make(map[string]string, len(keys))
	for i, cmd := range cmds {
		v, e := cmd.Result()
		if e != nil {
			continue
		}
		out[keys[i]] = v
	}
	return out, nil
}

func (s *RedisV2Store) LoadMoviesByText(ctx context.Context, texts []string) (map[string]MovieRecord, error) {
	if s == nil || s.rc == nil {
		return nil, redis.ErrClosed
	}
	entityPrefix := s.prefix + ":entity:movie:"

	keys := make([]string, 0, len(texts))
	uniq := make(map[string]struct{}, len(texts))
	for _, t := range texts {
		t = normalizeText(t)
		if t == "" {
			continue
		}
		if _, ok := uniq[t]; ok {
			continue
		}
		uniq[t] = struct{}{}
		keys = append(keys, entityPrefix+t)
	}
	rawByKey, err := s.getJSONByKeys(ctx, keys)
	if err != nil && err != redis.Nil {
		return nil, err
	}

	out := make(map[string]MovieRecord, len(rawByKey))
	for k, raw := range rawByKey {
		var rec MovieRecord
		if err := json.Unmarshal([]byte(raw), &rec); err != nil {
			continue
		}
		text := strings.TrimPrefix(k, entityPrefix)
		if text == "" {
			continue
		}
		out[text] = rec
	}
	return out, nil
}

func (s *RedisV2Store) LoadActorsByText(ctx context.Context, texts []string) (map[string]ActorRecord, error) {
	if s == nil || s.rc == nil {
		return nil, redis.ErrClosed
	}
	entityPrefix := s.prefix + ":entity:actor:"

	keys := make([]string, 0, len(texts))
	uniq := make(map[string]struct{}, len(texts))
	for _, t := range texts {
		t = normalizeText(t)
		if t == "" {
			continue
		}
		if _, ok := uniq[t]; ok {
			continue
		}
		uniq[t] = struct{}{}
		keys = append(keys, entityPrefix+t)
	}
	rawByKey, err := s.getJSONByKeys(ctx, keys)
	if err != nil && err != redis.Nil {
		return nil, err
	}

	out := make(map[string]ActorRecord, len(rawByKey))
	for k, raw := range rawByKey {
		var rec ActorRecord
		if err := json.Unmarshal([]byte(raw), &rec); err != nil {
			continue
		}
		text := strings.TrimPrefix(k, entityPrefix)
		if text == "" {
			continue
		}
		out[text] = rec
	}
	return out, nil
}

// Small helper for sane timeouts in CLI paths.
func withTimeout(parent context.Context, d time.Duration) (context.Context, context.CancelFunc) {
	if d <= 0 {
		return context.WithCancel(parent)
	}
	return context.WithTimeout(parent, d)
}

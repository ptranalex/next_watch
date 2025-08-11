***REMOVED******REMOVED*** Search suggestions performance: findings and plan

***REMOVED******REMOVED******REMOVED*** Context

We observed frequent warnings in production indicating slow substring searches in `search-api` suggestion engine:

```
Slow substring search: '<query>' took >100ms, found <n> matches
```

***REMOVED******REMOVED******REMOVED*** Current architecture (summary)

- Redis keys populated by CLI (`apps/search-api/src/search_api/cli/commands/redis.py`):
  - `zset suggestions` holds titles/words/prefixes for prefix lookup
  - `suggestions:<text>` → entity id
  - `entity:<type>:<name>` → JSON with rich entity data
- Retrieval (`search-api/src/search_api/services/suggestion_engine.py`):
  - Prefix path: currently uses `zrange("suggestions", 0, -1)` and filters client-side
  - Fallback substring path: SCAN over `entity:<type>:*<query>*` until limit reached

***REMOVED******REMOVED******REMOVED*** Symptoms

- P95/P99 spikes when `_get_substring_matches` runs, logging >100ms warnings
- Prefix path does O(N) fetch of the entire `suggestions` sorted set, increasing latency and memory

***REMOVED******REMOVED******REMOVED*** Likely root causes

- Inefficient prefix retrieval (full `zrange` + Python filter)
- Substring fallback scans broad keyspace; no strict time budget
- Occasional use of `KEYS` fallback path (unsafe/slow in prod) in older code paths
- No read-through caching for computed suggestions per query

***REMOVED******REMOVED******REMOVED*** Goals

- Reduce suggestion response P95/P99 substantially (<40–60ms typical)
- Bound worst-case latency for substring matching
- Keep infra simple unless substring quality demands more advanced indexing

***REMOVED******REMOVED*** Proposed improvements

***REMOVED******REMOVED******REMOVED*** Phase 1 — Quick wins (low-risk)

- Prefix lookup via lex range with server-side filtering and limit:
  - Use `ZRANGEBYLEX suggestions [<prefix> [<prefix>\xff LIMIT 0 <limit>` (or `zrange` with `bylex`)
- Remove `KEYS` fallback entirely; rely on `SCAN` only where unavoidable
- Add strict time budget to substring search (example: 60–80ms wall-time); bail early
- Parallelize scans per entity type (`movie`, `actor`, `director`) using `asyncio.gather`
- Add read-through cache for final suggestions per query (TTL 5–15 minutes): `cache:suggestions:<query>`
- Increase minimum query length for substring fallback in production (e.g., 4) and only trigger if prefix results < 3
- Cap SCAN iterations per request (e.g., ≤5 pages per entity type)

***REMOVED******REMOVED******REMOVED*** Phase 2 — Better indexing to avoid SCAN at runtime

- Build n-gram index during CLI population to support infix/substring efficiently:
  - For each important token, write trigrams to `idx:ng:3:<gram>` mapping to a capped candidate list (IDs or normalized names)
  - At runtime: fetch candidates from `idx:ng:3:<query[:3]>`, filter in-memory for actual substring, then hydrate
  - Keep per-gram candidate lists bounded (e.g., top 200 by popularity) to ensure predictable latency and memory

***REMOVED******REMOVED******REMOVED*** Phase 3 — Redis Stack RediSearch (optional, infra-dependent)

- Use RediSearch autocomplete and/or full-text index:
  - `FT.SUGADD`/`FT.SUGGET` for typeahead with prefix and fuzzy
  - If true infix required, use RediSearch index with trigram tokenization
  - Pros: built-in ranking, typo tolerance; Cons: infra change and migration

***REMOVED******REMOVED*** Implementation notes

***REMOVED******REMOVED******REMOVED*** Code changes (Phase 1)

- Replace client-side filtering with lexicographical range query:
  - `zrangebylex("suggestions", f"[{prefix}", f"[{prefix}\xff", start=0, num=limit)`
- Drop `KEYS` usage in any fallback path
- Add `time.monotonic()` deadline in `_get_substring_matches` and early return when exceeded
- Run entity-type scans concurrently and merge unique results up to limit
- Add Redis read-through cache in `get_entity_suggestions` with TTL from config
- Config-gate behavior in `SearchAPIConfig` (feature flags, limits, TTL)

***REMOVED******REMOVED******REMOVED*** CLI changes (Phase 2)

- During population, create `idx:ng:3:<gram>` entries for each token in titles/names
- Store IDs or normalized names; cap by popularity to bound list sizes
- Keep existing zset and `entity:*` for current prefix + hydration path

***REMOVED******REMOVED*** Testing and rollout

***REMOVED******REMOVED******REMOVED*** TDD/Test plan

- Unit tests for:
  - Lex range behavior and limits
  - No `KEYS` usage in suggestion paths
  - Substring deadline honored (returns partial results within budget)
  - Concurrency correctness and deduplication
  - Read-through cache set/get with TTL
- Integration tests:
  - Suggestion responses maintain correctness ordering and limits
  - Cache hit reduces latency on repeated queries

***REMOVED******REMOVED******REMOVED*** Metrics to monitor

- Suggestion endpoint latency P50/P95/P99
- Rate of "Slow substring search" warnings (should drop to near-zero)
- Redis CPU/network usage; ops per request
- Cache hit rate for `cache:suggestions:*`

***REMOVED******REMOVED******REMOVED*** Rollout plan

- Ship Phase 1 behind config flags; canary on a small % of traffic
- Verify metrics, then enable for all
- Evaluate substring quality; if gaps remain, proceed with Phase 2 or adopt RediSearch per infra constraints

***REMOVED******REMOVED*** Risks and mitigations

- Risk: Reduced substring coverage with stricter budgets → Mitigate by caching and Phase 2 indexing
- Risk: Redis memory growth due to cache/index → Set TTLs and cap candidate list sizes
- Risk: Behavior differences across Redis versions for lex commands → Provide tested fallback to `ZRANGEBYLEX`

***REMOVED******REMOVED*** TODO checklist

- [ ] Replace prefix path with `ZRANGEBYLEX` (limit supported)
- [ ] Remove `KEYS` fallback; keep `SCAN` only with deadline and page caps
- [ ] Add per-request time budget to `_get_substring_matches`
- [ ] Parallelize per-entity-type scans
- [ ] Add read-through cache with configurable TTL
- [ ] Config flags: `suggestion_substring_min_len`, `suggestion_substring_budget_ms`, `suggestion_cache_ttl`
- [ ] Tests: unit + integration for Phase 1
- [ ] Observability: dashboard panels for latency, warnings, cache hit-rate
- [ ] Evaluate Phase 2 n-gram index; size/latency trade-offs
- [ ] Decide on RediSearch adoption and infra timeline (if needed)

***REMOVED******REMOVED******REMOVED*** Search API CLI

Typer-based command-line interface for managing Search API operational tasks, primarily Redis-backed search suggestions.

***REMOVED******REMOVED******REMOVED*** Quick start

- Activate environment (required):

  ```bash
  cd apps/search-api
  hatch shell
  ```

- Run the CLI:

  - Via Hatch script:
    ```bash
    hatch run cli -- --help
    ```
  - Via installed console script:
    ```bash
    search-api --help
    ```
  - Via module:
    ```bash
    python -m search_api.cli --help
    ```

Notes:

- The CLI reads configuration from `search_api.config` and falls back to sensible defaults (e.g., Redis at `redis://localhost:6379/0`).
- You can override Redis with `--redis-url` on supported commands.

***REMOVED******REMOVED******REMOVED*** Commands

- version

  - Show CLI/package version.
  - Examples:
    ```bash
    search-api version
    hatch run version
    ```

- redis

  - Redis data management commands for search suggestions.

  - populate-suggestions

    - Fetch movies (and optionally actors/directors) from Backend API and load suggestion data into Redis.
    - Key options:
      - `--limit, -l` Max number of movies to load (ignored when `--fetch-all` is set)
      - `--fetch-all` Load all available movies from Backend API
      - `--clear/--no-clear` Clear existing suggestion data first (default: clear)
      - `--words/--no-words` Include individual words from titles (default: include)
      - `--min-word, -m` Minimum word length when indexing words (default: 3)
      - `--actors/--no-actors` Include actors (default: include)
      - `--directors/--no-directors` Include directors (default: include)
      - `--entity-types` Comma list to control entity types; overrides individual flags (e.g. `movie,actor,director`)
      - `--actor-limit` Max actors to fetch (default: 500)
      - `--director-limit` Max directors to fetch (default: 200)
      - `--batch-size` Pipeline batch size for Redis operations (default: 100)
      - `--redis-url, -r` Redis URL (defaults to config or localhost)
      - `--validate/--no-validate` Validate a sample of loaded data (default: validate)
      - `--verbose, -v` Show detailed output
    - Examples:
      ```bash
      search-api redis populate-suggestions --limit 5000
      search-api redis populate-suggestions --fetch-all --no-actors --batch-size 200
      search-api redis populate-suggestions --entity-types "movie,actor" --min-word 4
      search-api redis populate-suggestions --no-clear --verbose -r redis://localhost:6379/0
      ```

  - test-suggestions

    - Query Redis suggestions and print results for quick verification.
    - Options: `QUERY` (arg), `--limit/-l`, `--redis-url/-r`, `--verbose`.
    - Examples:
      ```bash
      search-api redis test-suggestions "star" --limit 10
      hatch run cli -- redis test-suggestions batman -l 8 -v
      ```

  - info
    - Show Redis connection status and counts for suggestion data.
    - Options: `--redis-url/-r`.
    - Examples:
      ```bash
      search-api redis info
      python -m search_api.cli redis info -r redis://localhost:6379/0
      ```

***REMOVED******REMOVED******REMOVED*** Development tips

- Helpful Hatch scripts (from `pyproject.toml`):

  ```bash
  hatch run cli             ***REMOVED*** python -m search_api.cli
  hatch run version         ***REMOVED*** python -m search_api.cli version
  hatch run index-suggestions  ***REMOVED*** python -m search_api.cli search index-suggestions (if available)
  ```

- Rich formatting and progress bars are used for visibility; add `-v/--verbose` for more detail.

***REMOVED******REMOVED******REMOVED*** Troubleshooting

- If Redis is unreachable, verify `--redis-url` or the configured Redis URL in environment/config.
- Backend API must be reachable for populate operations. Ensure its base URL is correctly configured in Search API settings.

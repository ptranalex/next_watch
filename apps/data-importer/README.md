***REMOVED*** Data Importer

This application provides tools to import movie and TV show data from external sources into the Next Watch database.

***REMOVED******REMOVED*** Features

- Import movies from TMDB (The Movie Database) with cast and crew information
- Import movie details from OMDB (Open Movie Database)
- Support for syncing by year range or importing specific movies by ID
- CLI interface with multiple commands
- Interactive shell for data exploration
- Detailed logging and error handling
- Bulk operations with progress tracking
- Customizable data transformation options
- Docker support for containerized deployment

***REMOVED******REMOVED*** Installation

***REMOVED******REMOVED******REMOVED*** Using Docker (Recommended for Production)

Build the Docker image from the monorepo root:

```bash
cd /path/to/next_watch
docker build -f apps/data-importer/Dockerfile -t data-importer .
```

Run with Docker:

```bash
***REMOVED*** Show help
docker run --rm data-importer --help

***REMOVED*** Sync movies with environment variables
docker run --rm \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  data-importer sync movies 2022 2023 --credits --save

***REMOVED*** Using docker-compose (from infra directory)
cd infra
docker-compose --profile sync up data-importer
```

***REMOVED******REMOVED******REMOVED*** Using Poetry (Development)

```bash
cd apps/data-importer
poetry install
```

***REMOVED******REMOVED******REMOVED*** Using Pip

```bash
cd apps/data-importer
pip install -e .
```

***REMOVED******REMOVED*** Usage

***REMOVED******REMOVED******REMOVED*** Environment Setup

Set your API keys as environment variables:

```bash
export TMDB_ACCESS_TOKEN="your_tmdb_access_token_here"
export OMDB_API_KEY="your_omdb_api_key_here"
export DATABASE_URL="postgresql://user:password@localhost:5432/nextwatch"
```

Alternatively, create a `.env` file in the project root with these values.

***REMOVED******REMOVED******REMOVED*** CLI Commands

***REMOVED******REMOVED******REMOVED******REMOVED*** Sync Movies by Year Range

```bash
***REMOVED*** Using local installation
data-importer sync movies 2022 2023 --credits --save

***REMOVED*** Using Docker
docker run --rm \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer sync movies 2022 2023 --credits --save
```

Options:

- `--limit`, `-l`: Maximum movies per year (default: 20)
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--save/--no-save`: Save movies to database (default: --no-save)
- `--credits/--no-credits`: Include cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output
- `--filter`: Filter movies by specified criteria (e.g., "vote_count>100")
- `--skip-existing`: Skip movies that already exist in the database

***REMOVED******REMOVED******REMOVED******REMOVED*** Import Movies by ID

```bash
***REMOVED*** Using local installation
data-importer import tmdb-id 550 634649 --credits --save

***REMOVED*** Using Docker
docker run --rm \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer import tmdb-id 550 634649 --credits --save
```

Options:

- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--save/--no-save`: Save movies to database (default: --no-save)
- `--credits/--no-credits`: Include cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED******REMOVED*** Import from File

```bash
***REMOVED*** Using local installation
data-importer import from-file movie_ids.txt --credits --save

***REMOVED*** Using Docker (with volume mount)
docker run --rm \
  -v $(pwd)/movie_ids.txt:/app/movie_ids.txt \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer import from-file /app/movie_ids.txt --credits --save
```

Options:

- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--save/--no-save`: Save movies to database (default: --no-save)
- `--credits/--no-credits`: Include cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output
- `--format`: Format of the input file (tmdb-id, imdb-id, title)

***REMOVED******REMOVED******REMOVED******REMOVED*** Update Existing Movies

```bash
***REMOVED*** Using local installation
data-importer update movies --credits

***REMOVED*** Using Docker
docker run --rm \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer update movies --credits
```

Options:

- `--all`: Update all movies in the database
- `--ids`: Comma-separated list of movie IDs to update
- `--since`: Update movies added since specified date (YYYY-MM-DD)
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--credits/--no-credits`: Update cast and crew information (default: --no-credits)
- `--verbose`, `-v`: Show detailed output

***REMOVED******REMOVED******REMOVED******REMOVED*** Interactive Shell

Launch an interactive shell to explore and manipulate data:

```bash
***REMOVED*** Using local installation
data-importer shell

***REMOVED*** Using Docker (interactive mode)
docker run --rm -it \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer shell
```

Options:

- `--config-dir`, `-c`: Configuration directory
- `--logs-dir`, `-l`: Directory to save log files
- `--data-dir`, `-d`: Directory for movie data files
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--imdb-api-key`, `-i`: IMDb API key (if not set as environment variable)
- `--omdb-api-key`, `-o`: OMDB API key (if not set as environment variable)
- `--verbose`, `-v`: Enable verbose logging
- `--quiet`, `-q`: Suppress non-essential output
- `--theme`, `-th`: Color theme for the shell (default, monokai, solarized, pastie, vs, manni, autumn, murphy, monochrome)
- `--plain`, `-p`: Use plain output without syntax highlighting

In the shell, you can use various functions:

```python
***REMOVED*** Get popular movies from TMDB
movies = run_async(tmdb_client.get_popular_movies())

***REMOVED*** Search for a movie
results = run_async(tmdb_client.search_movies("Inception"))

***REMOVED*** Get movie by ID
movie = run_async(tmdb_client.get_movie(550))

***REMOVED*** Get movie credits
credits = run_async(tmdb_client.get_movie_credits(550))

***REMOVED*** Save movie to database
db_movie = save_movie(movie, credits)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Interactive Mode (Experimental)

Launch an interactive interface for data import operations:

```bash
***REMOVED*** Using local installation
data-importer interactive

***REMOVED*** Using Docker (interactive mode)
docker run --rm -it \
  -e TMDB_ACCESS_TOKEN="your_token" \
  -e OMDB_API_KEY="your_key" \
  -e DATABASE_URL="your_db_url" \
  data-importer interactive
```

Options:

- `--config-dir`, `-c`: Configuration directory
- `--logs-dir`, `-l`: Directory to save log files
- `--tmdb-token`, `-t`: TMDB Bearer token (if not set as environment variable)
- `--omdb-key`, `-o`: OMDB API key (if not set as environment variable)
- `--verbose`, `-v`: Enable verbose logging
- `--quiet`, `-q`: Suppress non-essential output

Note: This feature is experimental and not fully implemented yet.

***REMOVED******REMOVED*** Docker Deployment

***REMOVED******REMOVED******REMOVED*** Production Deployment

The data-importer is designed to run as a utility service in the Next Watch infrastructure. It's configured in the docker-compose setup with specific profiles:

```bash
***REMOVED*** Run data sync with docker-compose
cd infra
docker-compose --profile sync up data-importer

***REMOVED*** Run one-time import job
docker-compose run --rm data-importer sync movies 2023 --credits --save
```

***REMOVED******REMOVED******REMOVED*** Docker Environment Variables

When running with Docker, you can configure the application using these environment variables:

```bash
***REMOVED*** API Configuration
TMDB_ACCESS_TOKEN=your_tmdb_token
OMDB_API_KEY=your_omdb_key

***REMOVED*** Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=nextwatch
POSTGRES_PASSWORD=your_password
POSTGRES_DB=nextwatch

***REMOVED*** Application Configuration
ENVIRONMENT=production
LOG_LEVEL=info
BATCH_SIZE=100
RATE_LIMIT_DELAY=1
MAX_RETRIES=3
```

***REMOVED******REMOVED******REMOVED*** Health Checks

The Docker container includes health checks to ensure the service is running properly:

```bash
***REMOVED*** Check container health
docker run --rm data-importer --help
```

***REMOVED******REMOVED*** API Key Configuration

The application requires API keys for external services:

- **TMDB Access Token**: Get from [The Movie Database](https://www.themoviedb.org/settings/api)
- **OMDB API Key**: Get from [OMDb API](https://www.omdbapi.com/apikey.aspx)

You can provide these keys either as command-line options or environment variables:

```bash
export TMDB_ACCESS_TOKEN="your_tmdb_access_token_here"
export OMDB_API_KEY="your_omdb_api_key_here"
```

***REMOVED******REMOVED******REMOVED*** Configuration File

You can also create a configuration file at `~/.data-importer/config.toml`:

```toml
[api]
tmdb_token = "your_tmdb_access_token_here"
omdb_key = "your_omdb_api_key_here"
imdb_key = "your_imdb_api_key_here"

[paths]
data_dir = "~/movie_data"
logs_dir = "~/logs/data-importer"

[defaults]
save = false
credits = true
limit = 50
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Project Structure

- `src/data_importer/`: Main package
  - `cli/`: CLI commands
    - `commands/`: Command implementations
    - `utils.py`: CLI utilities
  - `services/`: Service implementations
    - `tmdb.py`: TMDB API client
    - `omdb.py`: OMDB API client
    - `imdb.py`: IMDB API client
  - `sync/`: Data synchronization logic
    - `movie_sync.py`: Movie synchronization functions
  - `config/`: Application configuration
  - `models/`: Data models and transformations
  - `db/`: Database operations

***REMOVED******REMOVED******REMOVED*** Building Docker Image

To build the Docker image for development:

```bash
***REMOVED*** From monorepo root
docker build -f apps/data-importer/Dockerfile -t data-importer:dev .

***REMOVED*** Test the build
docker run --rm data-importer:dev --help
```

The Docker image uses a multi-stage Alpine Linux build for optimal size and security:

- **Builder stage**: Installs build dependencies and compiles the application
- **Runtime stage**: Contains only the necessary runtime dependencies and application code
- **Security**: Runs as a non-root user with proper file permissions
- **Integration**: Properly integrates with the shared `movie-storage` library from the monorepo

***REMOVED******REMOVED******REMOVED*** Testing

Run the test suite with:

```bash
***REMOVED*** Run all tests
pytest

***REMOVED*** Run with coverage report
pytest --cov=data_importer

***REMOVED*** Test Docker build
docker build -f apps/data-importer/Dockerfile -t data-importer:test .
docker run --rm data-importer:test --help
```

***REMOVED******REMOVED******REMOVED*** Adding Support for New Data Sources

To add a new data source:

1. Create a new client in the `services/` directory
2. Update the sync functions to use the new source
3. Add CLI commands to interact with the new source
4. Update the Docker image build if new dependencies are required

***REMOVED******REMOVED*** Troubleshooting

Common issues and solutions:

- **API Rate Limiting**: TMDB imposes rate limits. Use the `--sleep` option to add delay between requests.
- **Database Connection Issues**: Ensure the database URL is correctly set in your environment.
- **Missing Data**: Some movies may have incomplete data. Use the `--verbose` flag to see warnings.
- **Docker Build Issues**: Ensure you're building from the monorepo root with the correct Dockerfile path.
- **Permission Issues**: The Docker container runs as a non-root user. Ensure mounted volumes have appropriate permissions.

***REMOVED******REMOVED******REMOVED*** Docker-specific Troubleshooting

- **Build Context**: Always build from the monorepo root: `docker build -f apps/data-importer/Dockerfile .`
- **Volume Mounts**: When mounting files, ensure they're accessible by the container's `app` user (UID/GID 1000)
- **Network Access**: Ensure the container can reach the database and external APIs
- **Environment Variables**: Double-check that all required environment variables are set

***REMOVED******REMOVED*** License

MIT

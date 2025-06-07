***REMOVED*** ML API Commands

This module provides CLI commands for interacting with the ML API service, which is responsible for generating vector embeddings and providing other machine learning functionality for the Recommendation API.

***REMOVED******REMOVED*** Commands

***REMOVED******REMOVED******REMOVED*** `test-connection`

Test connectivity to the ML API service.

```bash
python -m recommendation_api.cli.main ml test-connection [OPTIONS]
```

Options:

- `--url, -u TEXT`: Custom ML API URL (overrides configuration)
- `--verbose, -v`: Show detailed information
- `--quiet, -q`: Suppress most console output

***REMOVED******REMOVED******REMOVED*** `generate-embedding`

Generate a vector embedding for a movie. This embedding can be used for similarity search and recommendations.

```bash
python -m recommendation_api.cli.main ml generate-embedding TITLE OVERVIEW [OPTIONS]
```

Arguments:

- `TITLE`: Movie title
- `OVERVIEW`: Movie overview/description

Options:

- `--genres, -g TEXT`: Comma-separated list of genres
- `--id TEXT`: Movie ID (default: "test-movie")
- `--url, -u TEXT`: Custom ML API URL (overrides configuration)
- `--verbose, -v`: Show detailed information
- `--quiet, -q`: Suppress most console output

***REMOVED******REMOVED*** Examples

Test connection to the ML API with verbose output:

```bash
python -m recommendation_api.cli.main ml test-connection --verbose
```

Generate an embedding for a test movie:

```bash
python -m recommendation_api.cli.main ml generate-embedding \
    "Inception" \
    "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O." \
    --genres "Action,Sci-Fi,Thriller" \
    --id "inception-2010"
```

***REMOVED******REMOVED*** Error Handling

If the ML API service is unavailable or returns an error, the commands will display detailed error information and exit with a non-zero status code. Use the `--verbose` flag to see additional troubleshooting tips.

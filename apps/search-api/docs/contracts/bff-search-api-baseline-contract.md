# BFF ↔ Search API Baseline Contract (current /api/v1)

This document captures the **current request/response shapes** the BFF relies on when calling the (Python) Search API.

Scope (called by BFF today):

- `GET /api/v1/search/suggestions`
- `GET /api/v1/search/suggestions/text`
- `GET /api/v1/search/all`
- `GET /health`

Notes:

- The Search API uses `fast_core.responses.ResponseBuilder` for most `/api/v1/search/*` endpoints, so responses are **enveloped** (e.g., `{query, results, metadata}` or `{results, pagination, metadata}`).
- BFF extracts fields like `results`, `metadata.total`, and `pagination.total` from these responses. Extra fields are tolerated.

---

## `GET /api/v1/search/suggestions` (basic suggestions)

### Request (query params)

- `query` (string, required): user input string
- `limit` (int, optional, default `10`, min `1`, max `50`)

### Response `200 OK`

Envelope (ResponseBuilder **search** pattern):

```json
{
  "query": "in",
  "results": [
    {
      "id": 123,
      "name": "Inception",
      "type": "movie",
      "image_path": "/poster.jpg"
    }
  ],
  "metadata": {
    "total": 1,
    "service_info": {
      "service_name": "search-api",
      "search_backend": "redis"
    },
    "api_version": "v1",
    "response_pattern": "search",
    "search_context": {
      "search_type": "suggestions",
      "suggestion_type": "basic"
    }
  }
}
```

`results[]` item shape (basic suggestion):

- `id` (int)
- `name` (string)
- `type` (string; e.g. `"movie"`, `"actor"`, `"genre"`)
- `image_path` (string|null)

BFF dependency:

- BFF reads `results` and `metadata.total`.

### Errors

- `422` validation error (FastAPI)
- `400` `{ "detail": "<message>" }` (SearchServiceException)
- `500` `{ "detail": "Internal server error" }` (unexpected)

---

## `GET /api/v1/search/suggestions/text` (rich text suggestions)

### Request (query params)

- `query` (string, required, min length `1`)
- `limit` (int, optional, default `10`, min `1`, max `50`)

### Response `200 OK`

Envelope (ResponseBuilder **search** pattern):

```json
{
  "query": "nap",
  "results": [
    {
      "text": "Napoleon",
      "type": "movie",
      "id": 456,
      "image_path": "/poster.jpg",
      "year": 2023,
      "popularity": 123.45,
      "is_partial": false,
      "search_type": "prefix",
      "additional_info": {
        "overview": "..."
      }
    }
  ],
  "metadata": {
    "total": 1,
    "service_info": {
      "service_name": "search-api",
      "search_backend": "redis"
    },
    "api_version": "v1",
    "response_pattern": "search",
    "search_context": {
      "search_type": "suggestions",
      "suggestion_type": "text"
    }
  }
}
```

`results[]` item shape (text suggestion):

- `text` (string)
- `type` (string; e.g. `"movie"`, `"actor"`, `"director"`)
- `id` (int|null)
- `image_path` (string|null)
- `year` (int|null)
- `popularity` (number|null)
- `is_partial` (bool)
- `search_type` (string; e.g. `"exact"`, `"prefix"`, `"word"`, `"contains"`, `"unknown"`)
- `additional_info` (object|null)

BFF dependency:

- BFF reads `results` and `metadata.total`.

### Errors

- `422` validation error (FastAPI)
- `400` `{ "detail": "<message>" }` (SearchServiceException)
- `500` `{ "detail": "Internal server error" }` (unexpected)

---

## `GET /api/v1/search/all` (multi-entity search; paginated)

### Request (query params)

- `query` (string, required)
- `page` (int, optional, default `1`, min `1`)
- `limit` (int, optional, default `20`, min `1`, max `100`)
- `types` (string[], optional): repeated query param (e.g. `types=movie&types=actor`)

### Response `200 OK`

Envelope (ResponseBuilder **paginated** pattern):

```json
{
  "results": [
    {
      "id": 456,
      "name": "Napoleon",
      "type": "movie",
      "image_path": "/poster.jpg",
      "year": 2023,
      "popularity": 123.45,
      "additional_info": {
        "overview": "..."
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "metadata": {
    "query": "napoleon",
    "filters_applied": {
      "types": ["movie"]
    },
    "service_info": {
      "service_name": "search-api",
      "search_backend": "redis"
    },
    "api_version": "v1",
    "response_pattern": "paginated",
    "search_context": {
      "search_type": "all_entities",
      "entity_types": ["movie"]
    }
  }
}
```

`results[]` item shape (entity search result):

- `id` (int)
- `name` (string)
- `type` (string)
- `image_path` (string|null)
- `year` (int|null)
- `popularity` (number|null)
- `additional_info` (object|null)

BFF dependency:

- BFF reads `results` and `pagination.total` (and relies on the presence of the standard pagination fields).

### Errors

- `422` validation error (FastAPI)
- `400` `{ "detail": "<message>" }` (SearchServiceException)
- `500` `{ "detail": "Internal server error" }` (unexpected)

---

## `GET /health` (service health)

### Request

No params.

### Response `200 OK` (healthy)

Typical response includes:

- `status` (string; `"healthy"` or `"unhealthy"`/`"error"`)
- `service` (string; `"search"`)
- `version` (string; currently `"0.1.0"`)
- `environment` (string)
- `timestamp` (RFC3339-ish string with `Z`)
- `external_services` (object)
- `search_features` (object)

Example (healthy, with dependency checks):

```json
{
  "status": "healthy",
  "service": "search",
  "version": "0.1.0",
  "environment": "dev",
  "timestamp": "2025-12-27T00:00:00Z",
  "checks": {
    "backend_api": {
      "status": "ok",
      "healthy": true,
      "response_time_ms": 12.3
    },
    "redis": { "status": "ok", "healthy": true, "response_time_ms": 3.2 }
  },
  "external_services": {
    "backend_api": "http://backend-api:8000",
    "redis": "redis://***:***@redis:6379/0"
  },
  "search_features": {
    "semantic_search": false,
    "search_analytics": true,
    "fuzzy_matching": true,
    "typo_tolerance": true
  }
}
```

### Response `503 Service Unavailable`

If critical dependencies are unhealthy, `status_code` becomes `503` and `status` becomes `"unhealthy"` or `"error"`.

BFF dependency:

- BFF only requires `status` (and logs `service`), but preserves additional fields.

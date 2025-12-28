package backend

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type Client struct {
	baseURL        string
	internalAPIKey string
	http           *http.Client
}

func New(baseURL string, timeout time.Duration, internalAPIKey string) *Client {
	baseURL = strings.TrimRight(strings.TrimSpace(baseURL), "/")
	if timeout <= 0 {
		timeout = 30 * time.Second
	}
	return &Client{
		baseURL:        baseURL,
		internalAPIKey: strings.TrimSpace(internalAPIKey),
		http: &http.Client{
			Timeout: timeout,
		},
	}
}

func (c *Client) ListMovies(ctx context.Context, page, limit int, sortBy string, sortDesc bool) (MoviesListResponse, error) {
	if sortBy == "" {
		sortBy = "imdb_rating"
	}
	u, err := c.buildURL("/api/v1/movies", map[string]string{
		"page":      fmt.Sprintf("%d", page),
		"limit":     fmt.Sprintf("%d", limit),
		"sort_by":   sortBy,
		"sort_desc": fmt.Sprintf("%t", sortDesc),
	})
	if err != nil {
		return MoviesListResponse{}, err
	}

	var out MoviesListResponse
	if err := c.doJSON(ctx, http.MethodGet, u, &out); err != nil {
		return MoviesListResponse{}, err
	}
	return out, nil
}

func (c *Client) ListActors(ctx context.Context, page, limit int) (ActorsListResponse, error) {
	u, err := c.buildURL("/api/v1/actors", map[string]string{
		"page":  fmt.Sprintf("%d", page),
		"limit": fmt.Sprintf("%d", limit),
	})
	if err != nil {
		return ActorsListResponse{}, err
	}

	var out ActorsListResponse
	if err := c.doJSON(ctx, http.MethodGet, u, &out); err != nil {
		return ActorsListResponse{}, err
	}
	return out, nil
}

func (c *Client) buildURL(path string, query map[string]string) (string, error) {
	raw := c.baseURL + "/" + strings.TrimLeft(path, "/")
	pu, err := url.Parse(raw)
	if err != nil {
		return "", err
	}
	q := pu.Query()
	for k, v := range query {
		if v != "" {
			q.Set(k, v)
		}
	}
	pu.RawQuery = q.Encode()
	return pu.String(), nil
}

func (c *Client) doJSON(ctx context.Context, method, url string, out any) error {
	req, err := http.NewRequestWithContext(ctx, method, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", "search-indexer-go/1.0")
	if c.internalAPIKey != "" {
		req.Header.Set("Internal-API-Key", c.internalAPIKey)
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return err
	}
	defer func() { _ = resp.Body.Close() }()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	if resp.StatusCode >= 400 {
		// keep error readable but bounded
		msg := strings.TrimSpace(string(body))
		if len(msg) > 500 {
			msg = msg[:500] + "..."
		}
		return fmt.Errorf("backend api error: %s: %s", resp.Status, msg)
	}

	if out == nil {
		return nil
	}
	if err := json.Unmarshal(body, out); err != nil {
		return fmt.Errorf("decode backend response: %w", err)
	}
	return nil
}

package redisclient

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

type Client struct {
	rc *redis.Client
}

func New(redisURL string) (*Client, error) {
	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		return nil, err
	}

	return &Client{rc: redis.NewClient(opts)}, nil
}

func (c *Client) Close() error {
	if c == nil || c.rc == nil {
		return nil
	}
	return c.rc.Close()
}

func (c *Client) Ping(ctx context.Context) (time.Duration, error) {
	if c == nil || c.rc == nil {
		return 0, redis.ErrClosed
	}
	start := time.Now()
	_, err := c.rc.Ping(ctx).Result()
	return time.Since(start), err
}

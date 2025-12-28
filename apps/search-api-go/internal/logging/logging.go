package logging

import (
	"io"
	"os"
	"strings"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

type Options struct {
	Env      string
	Level    string
	Service  string
	Out      io.Writer
	UseColor bool
}

func Setup(opts Options) {
	if opts.Out == nil {
		opts.Out = os.Stdout
	}

	level := parseLevel(opts.Level)
	zerolog.SetGlobalLevel(level)

	zerolog.TimeFieldFormat = time.RFC3339Nano

	var out io.Writer = opts.Out
	if opts.Env == "dev" {
		out = zerolog.ConsoleWriter{
			Out:        opts.Out,
			TimeFormat: time.RFC3339Nano,
			NoColor:    !opts.UseColor,
		}
	}

	logger := zerolog.New(out).
		With().
		Timestamp().
		Str("service", opts.Service).
		Str("env", opts.Env).
		Logger()

	log.Logger = logger
}

func parseLevel(s string) zerolog.Level {
	switch strings.ToLower(strings.TrimSpace(s)) {
	case "trace":
		return zerolog.TraceLevel
	case "debug":
		return zerolog.DebugLevel
	case "info", "":
		return zerolog.InfoLevel
	case "warn", "warning":
		return zerolog.WarnLevel
	case "error":
		return zerolog.ErrorLevel
	case "fatal":
		return zerolog.FatalLevel
	case "panic":
		return zerolog.PanicLevel
	default:
		return zerolog.InfoLevel
	}
}

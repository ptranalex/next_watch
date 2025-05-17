"use client";

import { useEffect, useState } from "react";
import { createLogger, loggerConfig, LogLevel } from "../../logging";

// Create component-specific logger with explicit group name
const logger = createLogger("MovieDataFetcher");

// Auto-detected group from calling function/file
const autoLogger = createLogger();

interface Movie {
  id: number;
  title: string;
  year: number;
}

export default function MovieDataFetcher() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [renderCount, setRenderCount] = useState(0);

  // Toggle logger demo
  const toggleDebugLogging = () => {
    if (logger.isEnabled()) {
      logger.info("Disabling debug logs");
      loggerConfig.disableGroup("MovieDataFetcher");
    } else {
      // This won't be seen until after enabling!
      loggerConfig.enableGroup("MovieDataFetcher");
      logger.info("Debug logs enabled");
    }
  };

  // Change log level demo
  const setVerboseLogging = () => {
    logger.info("Setting verbose logging (DEBUG level)");
    loggerConfig.setMinLevel(LogLevel.DEBUG);
  };

  const setMinimalLogging = () => {
    logger.info("Setting minimal logging (WARN level)");
    loggerConfig.setMinLevel(LogLevel.WARN);
  };

  // Toggle emoji demo
  const toggleEmoji = () => {
    const currentConfig = loggerConfig.getConfig();
    loggerConfig.setUseEmoji(!currentConfig.useEmoji);
    logger.info(
      `Emoji prefixes ${currentConfig.useEmoji ? "disabled" : "enabled"}`
    );
  };

  // Update render count to demonstrate log-once methods
  useEffect(() => {
    setRenderCount((prev) => prev + 1);
  }, [movies]);

  // Demonstrate log-once methods - these will only appear once in the console
  // despite multiple renders
  logger.debugOnce(
    "Component mounted - you'll see this debug message only once"
  );
  logger.infoOnce("Basic component info - this info appears only once");
  logger.warnOnce("Demo warning - this warning message appears only once");

  // Show auto-detected group in action
  autoLogger.infoOnce("This log comes from auto-detected group");

  // Log every render (to demonstrate the difference from log-once methods)
  logger.debug(`Component rendered (${renderCount} times)`);

  useEffect(() => {
    // Log component lifecycle
    logger.debug("Effect running - fetch movies");

    const fetchMovies = async () => {
      try {
        logger.info("Fetching movie data...");

        // Simulate API call with delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Mock data
        const mockMovies: Movie[] = [
          { id: 1, title: "The Matrix", year: 1999 },
          { id: 2, title: "Inception", year: 2010 },
          { id: 3, title: "Interstellar", year: 2014 },
        ];

        logger.debug("Response data:", mockMovies);

        // Check for data issues
        const missingTitles = mockMovies.filter((m) => !m.title);
        if (missingTitles.length > 0) {
          logger.warn("Some movies are missing titles:", missingTitles);
        }

        setMovies(mockMovies);
        logger.info("Movie data loaded successfully");
      } catch (err) {
        const error = err as Error;
        logger.error("Failed to fetch movies:", error);
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();

    return () => {
      logger.debug("Component unmounting");
    };
  }, []);

  if (loading) {
    logger.debug("Rendering loading state");
    return <div>Loading movies...</div>;
  }

  if (error) {
    logger.debug("Rendering error state", { error });
    return <div>Error loading movies: {error.message}</div>;
  }

  logger.debug("Rendering movie list", { count: movies.length });

  return (
    <div>
      <h2>Movies</h2>
      <p>Render count: {renderCount}</p>
      <p>
        <small>Check console to see log-once methods in action</small>
      </p>

      {/* Logging controls */}
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={toggleDebugLogging}>
          {logger.isEnabled() ? "Disable Logs" : "Enable Logs"}
        </button>
        <button onClick={setVerboseLogging} style={{ marginLeft: "0.5rem" }}>
          Verbose Logs
        </button>
        <button onClick={setMinimalLogging} style={{ marginLeft: "0.5rem" }}>
          Minimal Logs
        </button>
        <button onClick={toggleEmoji} style={{ marginLeft: "0.5rem" }}>
          Toggle Emoji
        </button>
        <button
          onClick={() => loggerConfig.clearLoggedMessages()}
          style={{ marginLeft: "0.5rem" }}
        >
          Reset Once Logs
        </button>
      </div>

      {/* Movie data */}
      <ul>
        {movies.map((movie) => (
          <li key={movie.id}>
            {movie.title} ({movie.year})
          </li>
        ))}
      </ul>

      {/* Add dev-only debug panel */}
      {logger.isEnabled() && (
        <div
          style={{
            marginTop: "2rem",
            padding: "1rem",
            border: "1px dashed ***REMOVED***666",
            background: "***REMOVED***f5f5f5",
          }}
        >
          <h3>Debug Panel</h3>
          <pre>{JSON.stringify(movies, null, 2)}</pre>
          <p>
            <small>This panel only shows when logging is enabled</small>
          </p>
        </div>
      )}
    </div>
  );
}

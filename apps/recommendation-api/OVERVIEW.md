✅ Architecture & Business Logic Summary (with existing movie DB)

🏗️ Architecture Overview
• FastAPI: API layer for exposing recommendation endpoints.
• PostgreSQL:
• Stores all movie metadata (title, genres, actors, ratings).
• Stores user actions (watched, liked, watchlist).
• Stores precomputed similarity data (MovieSimilarity).
• SentenceTransformer (MiniLM):
• Reads movies from PostgreSQL.
• Generates embeddings from title + genres + actors.
• Qdrant (via Docker):
• Stores movie embeddings.
• Enables fast similarity search (for similar movies and personalized recs).

⸻

📚 Business Logic Use Cases

1. Similar Movies (Content-Based)
   • Input: movie_id
   • Logic:
   • Fetch that movie’s embedding from Qdrant.
   • Run similarity search in Qdrant (top-N).
   • Filter results: IMDb rating > 7, same genre optional.
   • Alternative: read from precomputed MovieSimilarity table.

⸻

2. Personalized Recommendations (User-Driven)
   • Input: user_id
   • Logic:
   • Fetch watched + liked movie IDs.
   • Get vectors from Qdrant for those movies.
   • Compute user vector = average of those embeddings.
   • Query Qdrant with user vector → get top-N movie vectors.
   • Filter out movies already watched or liked.
   • Filter by rating or genre if needed.
   • Save results into UserRecommendation table (optional).

⸻

3. Non-Authenticated Recommendations
   • Input: no user info
   • Logic:
   • Serve fallback based on:
   • Trending movies (most views/likes in last X days).
   • Top-rated content per genre.
   • Data fetched from PostgreSQL or Redis cache.

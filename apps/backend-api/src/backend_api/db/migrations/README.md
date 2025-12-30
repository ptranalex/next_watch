# Database Migrations

This directory contains database migration scripts for the Backend API. Migrations are used to manage database schema changes in a version-controlled, repeatable manner.

## Overview

The migration system allows you to:

- Apply incremental database schema changes
- Track which migrations have been applied
- Rollback changes when needed
- Maintain database consistency across environments

## Migration Files

Migrations are numbered sequentially and follow the naming pattern: `XXX_description.py`

### Current Migrations

| Migration                                        | Description                                        | Purpose                                                              |
| ------------------------------------------------ | -------------------------------------------------- | -------------------------------------------------------------------- |
| `001_create_initial_tables.py`                   | Create initial movie and genre tables              | Sets up the core movie and genre tables with basic movie information |
| `002_add_credits_and_extended_movie_fields.py`   | Add Credits table and extend Movie fields          | Adds cast/crew information and additional TMDB movie fields          |
| `003_update_budget_revenue_to_bigint.py`         | Update budget and revenue fields to BIGINT         | Handles larger financial values for blockbuster movies               |
| `004_rename_moviegenrelink_table.py`             | Rename moviegenrelink table to movie_genre_link    | Ensures consistent naming conventions                                |
| `005_add_ratings_and_awards.py`                  | Add Rotten Tomatoes, Metacritic ratings and awards | Extends movie rating information                                     |
| `006_add_trailer_table.py`                       | Add trailer table for storing movie trailers       | Stores YouTube trailer keys and metadata                             |
| `007_add_users_table.py`                         | Add users table for authentication                 | User management and authentication support                           |
| `008_add_user_movie_interactions_table.py`       | Add user movie interactions                        | Watchlist, watched status, and user preferences                      |
| `009_add_performance_optimization_indexes.py`    | Add performance optimization indexes               | Database performance improvements for common queries                 |
| `010_create_movie_metadata_materialized_view.py` | Create materialized view for movie metadata        | Precomputes and optimizes bulk metadata access                       |
| `011_add_credit_director_index.py`               | Add partial covering index for director lookups    | Speeds up `Directing/Director` by `movie_id` queries                 |

## Migration Structure

Each migration file contains:

```python
"""Migration description."""

from typing import Optional
from sqlalchemy.engine import Engine
from sqlalchemy import text

from backend_api.config.app import Config
from backend_api.config.logging import get_logger

# Migration identification
MIGRATION_ID = "XXX_migration_name"
MIGRATION_DESCRIPTION = "Brief description"

logger = get_logger(__name__)

def upgrade(engine: Engine, config: Optional[Config] = None) -> None:
    """Apply the migration."""
    # Migration logic here

def downgrade(engine: Engine, config: Optional[Config] = None) -> None:
    """Revert the migration."""
    # Rollback logic here
```

## Running Migrations

### Apply All Pending Migrations

```bash
python -m backend_api.cli database migrate
```

### Apply Migrations with Verbose Output

```bash
python -m backend_api.cli database migrate --verbose
```

### Check Migration Status

```bash
python -m backend_api.cli database status
```

## Rolling Back Migrations

### Rollback One Migration

```bash
python -m backend_api.cli database downgrade --steps 1
```

### Rollback to Specific Migration

```bash
python -m backend_api.cli database downgrade --target 008_add_user_movie_interactions_table
```

### Rollback All Migrations (⚠️ Destructive)

```bash
python -m backend_api.cli database downgrade --all
```

## Creating New Migrations

1. **Determine the next migration number** by looking at existing migrations
2. **Create a new file** following the naming pattern: `XXX_description.py`
3. **Use the migration template** shown above
4. **Implement both `upgrade` and `downgrade` functions**
5. **Test the migration** in a development environment

### Migration Best Practices

#### ✅ Do's

- **Always implement both upgrade and downgrade functions**
- **Use transactions** to ensure atomicity
- **Include descriptive migration IDs and descriptions**
- **Test migrations thoroughly** before applying to production
- **Use `IF EXISTS` and `IF NOT EXISTS` clauses** for idempotent operations
- **Add proper indexes** for performance-critical queries
- **Recording applied migrations is automatic**: The migration runner will insert a record into the `migrations` table after a successful `upgrade()` using an idempotent upsert. You may still insert manually within a migration for clarity; duplicates are ignored.
- **Removing migration records on downgrade is automatic**: The CLI downgrade flow deletes the corresponding `migrations` record after a successful `downgrade()`. You don't need to delete it inside the migration; doing so is harmless (a second delete is a no-op).

#### ❌ Don'ts

- **Don't modify existing migrations** once they've been applied
- **Don't create destructive migrations** without careful consideration
- **Don't forget to handle edge cases** (empty tables, missing columns, etc.)
- **Don't create migrations that depend on application code**
- **Don't skip testing downgrades**

### Example: Adding a New Table

```python
"""Migration to add example table."""

from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Optional

from backend_api.config.app import Config
from backend_api.config.logging import get_logger

MIGRATION_ID = "011_add_example_table"
MIGRATION_DESCRIPTION = "Add example table for demonstration"

logger = get_logger(__name__)

def upgrade(engine: Engine, config: Optional[Config] = None) -> None:
    """Create example table."""
    logger.info("Creating example table")

    with engine.begin() as conn:
        # Create table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS example (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Add index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_example_name ON example(name)
        """))

        # Record migration
        conn.execute(text("""
            INSERT INTO migrations (id, description)
            VALUES (:id, :description)
        """), {
            "id": MIGRATION_ID,
            "description": MIGRATION_DESCRIPTION
        })

    logger.info("Example table created successfully")

def downgrade(engine: Engine, config: Optional[Config] = None) -> None:
    """Drop example table."""
    logger.info("Dropping example table")

    with engine.begin() as conn:
        # Drop table
        conn.execute(text("DROP TABLE IF EXISTS example"))

        # Remove migration record
        conn.execute(text("""
            DELETE FROM migrations WHERE id = :id
        """), {"id": MIGRATION_ID})

    logger.info("Example table dropped successfully")
```

## Performance Considerations

### Indexing Strategy

The migration system includes several performance optimizations:

- **Composite indexes** for multi-column queries
- **Partial indexes** for filtered queries (e.g., `department = 'Acting'`)
- **Trigram indexes** for text search capabilities
- **Foreign key indexes** for relationship queries

### Query Optimization Examples

Migration `010_add_credit_department_job_index.py` specifically addresses slow queries like:

```sql
-- Before: Slow query (117ms)
SELECT c.name, c.department, c.job
FROM credit c
WHERE c.movie_id = ?
AND c.department IN ('Directing', 'Writing')
AND c.job IN ('Director', 'Screenplay')

-- After: Optimized with composite index (< 5ms expected)
-- Uses idx_credit_movie_dept_job and idx_credit_directors_writers
```

## Database Schema Evolution

### Schema Versioning

- Each migration increments the database schema version
- The `migrations` table tracks applied migrations and timestamps
- Migrations are applied in sequential order
- No migration should be skipped or applied out of order

### Environment Consistency

- Development, staging, and production should use the same migrations
- Always test migrations in a staging environment first
- Use database backups before applying migrations in production

## Troubleshooting

### Common Issues

1. **Migration fails partway through**

   - Check database logs for specific error messages
   - Ensure sufficient database permissions
   - Verify database connectivity

2. **Migration already applied error**

   - Check the `migrations` table for existing records
   - Use `--force` flag if migration needs to be re-run (⚠️ dangerous)

3. **Downgrade fails**
   - Ensure downgrade function is properly implemented
   - Check for dependent data that prevents rollback

### Recovery Procedures

1. **If migration fails during upgrade:**

   ```sql
   -- Check which migrations are recorded
   SELECT * FROM migrations ORDER BY applied_at;

   -- Manually remove failed migration record if needed
   DELETE FROM migrations WHERE id = 'XXX_failed_migration';
   ```

2. **If database is in inconsistent state:**
   - Restore from backup
   - Re-apply migrations from known good state
   - Contact database administrator if needed

## Related Documentation

- [Database Operations Guide](../operations/README.md)
- [API Configuration](../../config/README.md)
- [CLI Commands](../../cli/README.md)

## Support

For migration-related issues:

1. Check the logs for detailed error messages
2. Review this documentation for common solutions
3. Test in development environment first
4. Contact the development team for complex issues

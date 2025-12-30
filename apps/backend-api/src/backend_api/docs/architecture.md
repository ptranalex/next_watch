# Backend Architecture: CQRS Pattern

## Overview

This application follows the Command Query Responsibility Segregation (CQRS) pattern, which separates read and write operations:

- **Commands (Services)**: Handle state-changing operations (write, update, delete)
- **Queries**: Handle data retrieval operations (read) optimized for specific views

## When to Use Services vs Queries

### Use Services When:

1. **Modifying State**: Creating, updating, or deleting records
2. **Implementing Business Rules**: Applying domain logic or validation
3. **Managing Transactions**: Operations that must be atomic
4. **Orchestrating Complex Operations**: Coordinating multiple steps
5. **Handling Events**: Publishing domain events after state changes

```python
# Example Service Method
def toggle_movie_watched(user_id: int, movie_id: int) -> UserMovieInteraction:
    """
    Business logic for toggling watched status.
    - Validates entities
    - Performs state change
    - Can trigger events
    """
```

### Use Queries When:

1. **Retrieving Data**: Complex read operations without state changes
2. **Optimizing Read Paths**: SQL optimizations, joins, aggregations
3. **Data Transformations**: Reshaping data for specific views
4. **Complex Filtering/Searching**: Custom search implementations
5. **Reporting/Analytics**: Aggregated statistics

```python
# Example Query Method
def get_user_recommended_movies(user_id: int, limit: int) -> List[Movie]:
    """
    Complex read operation optimized for this specific use case.
    - Can use custom SQL
    - Optimized for performance
    - Returns read-only data
    """
```

## Standard Error Handling

All services and queries should use standardized error types:

1. `ResourceNotFoundError`: When a requested entity doesn't exist
2. `ValidationError`: When input data is invalid
3. `ConflictError`: When an operation conflicts with current state
4. `PermissionError`: When a user lacks required permissions
5. `ServiceError`: Base class for all other service errors

Routes translate these errors to appropriate HTTP status codes.

## Interface Guidelines

- Services and queries should have clear method signatures with type hints
- Methods should have comprehensive docstrings
- Input validation should happen at the beginning of methods
- Services should not return HTTP-specific responses

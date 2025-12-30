# BFF API Schemas

This module defines all data models (schemas) used for request validation, response serialization, and data transfer between components.

## Structure

The schemas module is organized by domain:

```
bff_api/schemas/
│
├── __init__.py                 # Package initialization
├── auth_schemas.py             # Authentication and authorization schemas
├── screen_schemas.py           # Movie, TV show, and media content schemas
└── user_interaction_schemas.py # User ratings, reviews, and interactions schemas
```

## Schema Types

The schemas module contains several types of models:

1. **Request Models**: Validate and parse incoming request data
2. **Response Models**: Define and validate outgoing response data
3. **Internal Models**: Used for data transfer between components
4. **Enum Classes**: Define allowed values for certain fields

## Implementation

All schemas are implemented using Pydantic models, which provide:

- Runtime type checking
- Data validation
- JSON serialization/deserialization
- OpenAPI schema generation
- Automatic documentation

Example:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }
```

## Validation

Schemas implement validation rules including:

- Type validation (string, integer, boolean, etc.)
- Range validation (min/max values)
- String pattern validation (regex)
- Enum validation (restricted choices)
- Custom validators for complex rules

Example of custom validation:

```python
from pydantic import BaseModel, Field, validator

class MovieRating(BaseModel):
    """Schema for submitting a movie rating."""

    movie_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=10)

    @validator("rating")
    def validate_rating(cls, v):
        """Ensure rating is between 1 and 10."""
        if not 1 <= v <= 10:
            raise ValueError("Rating must be between 1 and 10")
        return v
```

## Schema Inheritance

Schemas use inheritance to create hierarchies and avoid duplication:

- Base classes define common fields
- Derived classes add specific fields
- Response models often extend request models

Example:

```python
class UserBase(BaseModel):
    """Base schema with common user fields."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user creation, adds password."""
    password: str

class UserResponse(UserBase):
    """Schema for user responses, adds id and timestamps."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## Design Principles

1. **Single Responsibility**: Each schema represents a single data structure
2. **Validation at Boundaries**: Validate data as it enters and leaves the system
3. **Self-Documentation**: Schemas document their own structure and constraints
4. **Consistency**: Similar entities have similar schema structures
5. **Separation**: Input and output schemas are separated to control visibility

## Extension Guidelines

When adding new schemas:

1. Identify the appropriate domain file or create a new one
2. Define the schema using Pydantic models
3. Include appropriate validation rules
4. Add examples for documentation
5. Follow naming conventions

## Best Practices

- Include comprehensive field descriptions
- Add examples for all schemas
- Use appropriate field constraints
- Include custom validators for complex rules
- Keep schemas focused and minimal
- Use inheritance to avoid duplication
- Follow consistent naming conventions:
  - `EntityCreate` for creation requests
  - `EntityUpdate` for update requests
  - `EntityResponse` for responses
  - `EntityBase` for common fields

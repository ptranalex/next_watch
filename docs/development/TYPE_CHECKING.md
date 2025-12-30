# Type Checking Standards

This project uses strict type checking with mypy across Python services.

## Configuration

- All type checking configuration is stored in each service's `pyproject.toml`
- We use Python 3.12 for type checking
- We enforce consistent type checking rules across core API services (BFF API, Backend API, Recommendation API), including:
  - `disallow_untyped_defs = true` - all functions must have type annotations
  - `disallow_incomplete_defs = true` - no partial type annotations
  - `check_untyped_defs = true` - check bodies of functions without annotations
  - `no_implicit_optional = true` - don’t treat None as implicit Optional
  - `disallow_untyped_calls = true` - can’t call functions without type hints
  - `disallow_any_generics = true` - avoid `Any` in generics (e.g. `List[Any]`)
  - `disallow_subclassing_any = true` - can’t subclass `Any`
  - `disallow_untyped_globals = true` - module-level vars must have type annotations
  - full warnings for redundant casts, unused ignores, unreachable code, etc.

## Type Annotations Style

```python
# Use explicit imports from typing
from typing import Any, Dict, List, Optional, TypeVar

# All module-level variables must have explicit type annotations
DEFAULT_TIMEOUT: int = 30
RETRY_COUNT: int = 3

def process_data(input_value: str, count: int = 0) -> List[Dict[str, Any]]:
    ...

T = TypeVar("T")

def get_item(item_id: str) -> Optional[T]:
    ...
```

## Enforcement

Type checking is enforced through:

1. Pre-commit hooks (see `.pre-commit-config.yaml`)
2. CI pipeline checks
3. Code reviews

## Running Type Checks

```bash
# Check a specific service
cd apps/bff-api && python -m mypy src/

# Or for recommendation-api
cd apps/recommendation-api && python -m mypy src/
```



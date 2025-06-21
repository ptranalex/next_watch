"""Basic FastAPI application example using Fast Core.

This example demonstrates how to create a FastAPI application
using the Fast Core library with all the standard components.
"""

import uvicorn
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

***REMOVED*** Import Fast Core components
from fast_core import (
    APIException,
    AppOptions,
    BaseRouter,
    FastAPIConfig,
    HealthCheck,
    PaginationParams,
    ResourceNotFoundException,
    ValidationException,
    create_app,
    create_error_response,
    create_success_response,
    get_pagination_params,
    paginate_results,
    setup_health_checks,
)

try:
    from fast_core.dependencies.common import get_request_id, get_settings
    from fast_core.errors import setup_exception_handlers
    from fast_core.middleware import setup_middleware
except ImportError:
    ***REMOVED*** Fallback if dependencies are not available
    pass


***REMOVED*** Configuration
class AppConfig(FastAPIConfig):
    """Application configuration."""

    service_name: str = "Fast Core Example"
    version: str = "0.1.0"
    debug: bool = True

    ***REMOVED*** CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True

    ***REMOVED*** Logging settings
    log_requests: bool = True
    log_responses: bool = True


***REMOVED*** Data models
class ItemCreate(BaseModel):
    """Model for creating items."""

    name: str
    description: str = ""
    price: float


class Item(BaseModel):
    """Item model."""

    id: int
    name: str
    description: str
    price: float


class ItemList(BaseModel):
    """List of items with pagination."""

    items: list[Item]
    total: int


***REMOVED*** In-memory data store
items_db = [
    Item(id=1, name="Laptop", description="Gaming laptop", price=1299.99),
    Item(id=2, name="Mouse", description="Gaming mouse", price=79.99),
    Item(id=3, name="Keyboard", description="Mechanical keyboard", price=149.99),
    Item(id=4, name="Monitor", description="4K monitor", price=399.99),
    Item(id=5, name="Headphones", description="Wireless headphones", price=199.99),
]


***REMOVED*** Create routers
api_router = BaseRouter(prefix="/api/v1", tags=["API"])


***REMOVED*** Health check functions
async def check_application() -> bool:
    """Check application health."""
    ***REMOVED*** Simple check - in real app this would check database, etc.
    return len(items_db) >= 0


***REMOVED*** Routes
@api_router.get("/items", response_model=dict)
async def list_items(
    pagination: PaginationParams = Depends(get_pagination_params),
    request_id: str = Depends(get_request_id) if "get_request_id" in globals() else None,
):
    """List items with pagination."""
    try:
        ***REMOVED*** Calculate pagination
        start = pagination.offset
        end = start + pagination.page_size
        paginated_items = items_db[start:end]

        ***REMOVED*** Create response
        return paginate_results(
            data=[item.dict() for item in paginated_items],
            pagination=pagination,
            total_items=len(items_db),
        )
    except Exception as e:
        raise APIException(
            status_code=500,
            detail="Failed to retrieve items",
            error_code="ITEMS_RETRIEVAL_ERROR",
        )


@api_router.get("/items/{item_id}", response_model=dict)
async def get_item(item_id: int):
    """Get a specific item."""
    item = next((item for item in items_db if item.id == item_id), None)
    if not item:
        raise ResourceNotFoundException(
            detail="Item not found",
            resource_type="item",
            resource_id=str(item_id),
        )

    return create_success_response(
        message="Item retrieved successfully",
        data=item.dict(),
    )


@api_router.post("/items", response_model=dict, status_code=201)
async def create_item(item_data: ItemCreate):
    """Create a new item."""
    ***REMOVED*** Validate data
    if item_data.price <= 0:
        raise ValidationException(
            detail="Price must be positive",
            field_errors={"price": "Must be greater than 0"},
        )

    ***REMOVED*** Create new item
    new_id = max((item.id for item in items_db), default=0) + 1
    new_item = Item(
        id=new_id,
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
    )

    items_db.append(new_item)

    return create_success_response(
        message="Item created successfully",
        data=new_item.dict(),
    )


@api_router.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: int):
    """Delete an item."""
    item_index = next((i for i, item in enumerate(items_db) if item.id == item_id), None)
    if item_index is None:
        raise ResourceNotFoundException(
            detail="Item not found",
            resource_type="item",
            resource_id=str(item_id),
        )

    deleted_item = items_db.pop(item_index)

    return create_success_response(
        message="Item deleted successfully",
        data=deleted_item.dict(),
    )


***REMOVED*** Create application
def create_example_app():
    """Create the example FastAPI application."""
    ***REMOVED*** Configuration
    settings = AppConfig()

    ***REMOVED*** Application options
    options = AppOptions(
        middleware=True,
        exception_handlers=True,
        health_checks=True,
        cors=True,
        docs=True,
    )

    ***REMOVED*** Create app
    app = create_app(
        settings=settings,
        title=settings.service_name,
        description="Example FastAPI application using Fast Core",
        version=settings.version,
        options=options,
        routers=[api_router],
    )

    ***REMOVED*** Setup health checks
    if "setup_health_checks" in globals():
        health_check = setup_health_checks(app, settings)
        health_check.add_check("application", check_application)

    return app


***REMOVED*** Create the app instance
app = create_example_app()


if __name__ == "__main__":
    ***REMOVED*** Run the application
    uvicorn.run(
        "basic_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

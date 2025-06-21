"""Advanced FastAPI application example using Fast Core.

This example demonstrates advanced features of the Fast Core library including:
- JWT authentication and authorization
- Rate limiting
- Comprehensive error handling
- Custom middleware
- Health checks with dependencies
- API versioning
- Caching
- Security features
"""

import asyncio
import time
from typing import Optional

import uvicorn
from fastapi import Depends, Query
from pydantic import BaseModel, Field

***REMOVED*** Import Fast Core components
from fast_core import (  ***REMOVED*** Exceptions; Responses; Health checks; Security
    APIException,
    APIVersion,
    AppOptions,
    AuthenticationException,
    AuthorizationException,
    BaseRouter,
    BusinessLogicException,
    ConflictException,
    FastAPIConfig,
    HealthCheck,
    JWTConfig,
    JWTManager,
    MemoryRateLimiter,
    PaginationParams,
    RateLimiter,
    RateLimitException,
    ResourceNotFoundException,
    TokenData,
    ValidationException,
    VersionedRouter,
    create_app,
    create_error_response,
    create_paginated_response,
    create_success_response,
    get_pagination_params,
    paginate_results,
    rate_limit,
    setup_health_checks,
)

try:
    from fast_core.dependencies.auth import get_current_user, require_auth
    from fast_core.dependencies.cache import get_cache_service
    from fast_core.dependencies.common import get_request_id, get_settings
    from fast_core.errors import setup_exception_handlers
    from fast_core.middleware import setup_middleware
except ImportError as e:
    print(f"Some dependencies not available: {e}")


***REMOVED*** Configuration
class AdvancedAppConfig(FastAPIConfig):
    """Advanced application configuration."""

    service_name: str = "Advanced Fast Core Example"
    version: str = "1.0.0"
    debug: bool = True

    ***REMOVED*** Security settings
    secret_key: str = "super-secret-key-for-demo-only"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    ***REMOVED*** Rate limiting
    enable_rate_limiting: bool = True
    requests_per_minute: int = 100

    ***REMOVED*** CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True

    ***REMOVED*** Caching
    enable_caching: bool = True
    cache_ttl: int = 300  ***REMOVED*** 5 minutes

    ***REMOVED*** Monitoring
    enable_health_checks: bool = True
    health_check_interval: int = 30


***REMOVED*** Data models
class User(BaseModel):
    """User model."""

    id: int
    username: str
    email: str
    roles: list[str] = Field(default_factory=list)
    is_active: bool = True


class UserCreate(BaseModel):
    """Model for creating users."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8)
    roles: list[str] = Field(default_factory=list)


class UserLogin(BaseModel):
    """Model for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class Product(BaseModel):
    """Product model."""

    id: int
    name: str
    description: str
    price: float
    category: str
    in_stock: bool = True
    created_at: Optional[str] = None


class ProductCreate(BaseModel):
    """Model for creating products."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    in_stock: bool = True


***REMOVED*** In-memory data stores
users_db = [
    User(id=1, username="admin", email="admin@example.com", roles=["admin", "user"]),
    User(id=2, username="user", email="user@example.com", roles=["user"]),
    User(id=3, username="manager", email="manager@example.com", roles=["manager", "user"]),
]

products_db = [
    Product(
        id=1,
        name="Laptop",
        description="High-performance laptop",
        price=1299.99,
        category="Electronics",
    ),
    Product(
        id=2, name="Coffee Mug", description="Ceramic coffee mug", price=15.99, category="Kitchen"
    ),
    Product(id=3, name="Notebook", description="Spiral notebook", price=5.99, category="Office"),
    Product(
        id=4,
        name="Smartphone",
        description="Latest smartphone",
        price=799.99,
        category="Electronics",
    ),
    Product(
        id=5,
        name="Desk Chair",
        description="Ergonomic office chair",
        price=249.99,
        category="Furniture",
    ),
]

***REMOVED*** Mock password storage (in real app, use proper hashing)
user_passwords = {
    "admin": "admin123",
    "user": "user123",
    "manager": "manager123",
}


***REMOVED*** JWT Manager setup
def create_jwt_manager(settings: AdvancedAppConfig) -> JWTManager:
    """Create JWT manager."""
    config = JWTConfig(
        secret_key=settings.secret_key,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )
    return JWTManager(config)


***REMOVED*** Rate limiter setup
rate_limiter = MemoryRateLimiter(requests_per_minute=100)


***REMOVED*** Authentication functions
async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user credentials."""
    user = next((u for u in users_db if u.username == username), None)
    if not user or not user.is_active:
        return None

    ***REMOVED*** Check password (in real app, use proper hashing)
    if user_passwords.get(username) != password:
        return None

    return user


async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    return next((u for u in users_db if u.username == username), None)


***REMOVED*** Health check functions
async def check_database() -> bool:
    """Check database connection."""
    ***REMOVED*** Simulate database check
    await asyncio.sleep(0.1)
    return len(users_db) > 0 and len(products_db) > 0


async def check_external_service() -> bool:
    """Check external service."""
    ***REMOVED*** Simulate external service check
    await asyncio.sleep(0.1)
    return True


async def check_cache() -> bool:
    """Check cache service."""
    ***REMOVED*** Simulate cache check
    await asyncio.sleep(0.05)
    return True


***REMOVED*** Create routers with versioning
auth_router = VersionedRouter(
    prefix="/auth",
    tags=["Authentication"],
    version=APIVersion.V1,
)

products_router = VersionedRouter(
    prefix="/products",
    tags=["Products"],
    version=APIVersion.V1,
)

admin_router = VersionedRouter(
    prefix="/admin",
    tags=["Administration"],
    version=APIVersion.V1,
)


***REMOVED*** Authentication routes
@auth_router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    settings: AdvancedAppConfig = Depends(get_settings),
):
    """Login user and return tokens."""
    ***REMOVED*** Rate limiting
    if await rate_limiter.is_rate_limited("login", "global"):
        raise RateLimitException(
            detail="Too many login attempts",
            retry_after=60,
        )

    ***REMOVED*** Authenticate user
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise AuthenticationException(
            detail="Invalid username or password",
            error_code="INVALID_CREDENTIALS",
        )

    ***REMOVED*** Create JWT manager and generate tokens
    jwt_manager = create_jwt_manager(settings)
    token_data = TokenData(
        sub=user.username,
        user_id=user.id,
        roles=user.roles,
    )

    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@auth_router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(require_auth),
):
    """Get current user information."""
    return create_success_response(
        message="User information retrieved",
        data=current_user.dict(),
    )


***REMOVED*** Product routes
@products_router.get("", response_model=dict)
@rate_limit(requests=50, window=60)  ***REMOVED*** 50 requests per minute
async def list_products(
    pagination: PaginationParams = Depends(get_pagination_params),
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
):
    """List products with filtering and pagination."""
    try:
        ***REMOVED*** Apply filters
        filtered_products = products_db

        if category:
            filtered_products = [
                p for p in filtered_products if p.category.lower() == category.lower()
            ]

        if in_stock is not None:
            filtered_products = [p for p in filtered_products if p.in_stock == in_stock]

        if search:
            search_lower = search.lower()
            filtered_products = [
                p
                for p in filtered_products
                if search_lower in p.name.lower() or search_lower in p.description.lower()
            ]

        ***REMOVED*** Apply pagination
        start = pagination.offset
        end = start + pagination.page_size
        paginated_products = filtered_products[start:end]

        return create_paginated_response(
            data=[product.dict() for product in paginated_products],
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=len(filtered_products),
        )

    except Exception as e:
        raise APIException(
            status_code=500,
            detail="Failed to retrieve products",
            error_code="PRODUCTS_RETRIEVAL_ERROR",
            context={"error": str(e)},
        )


@products_router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int):
    """Get a specific product."""
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise ResourceNotFoundException(
            detail="Product not found",
            resource_type="product",
            resource_id=str(product_id),
        )

    return create_success_response(
        message="Product retrieved successfully",
        data=product.dict(),
    )


@products_router.post("", response_model=dict, status_code=201)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_auth),
):
    """Create a new product (requires authentication)."""
    ***REMOVED*** Check if user has permission
    if "admin" not in current_user.roles and "manager" not in current_user.roles:
        raise AuthorizationException(
            detail="Insufficient permissions to create products",
            required_permissions=["admin", "manager"],
        )

    ***REMOVED*** Check for duplicate product name
    existing_product = next(
        (p for p in products_db if p.name.lower() == product_data.name.lower()), None
    )
    if existing_product:
        raise ConflictException(
            detail="Product with this name already exists",
            conflicting_resource={"id": existing_product.id, "name": existing_product.name},
        )

    ***REMOVED*** Business logic validation
    if product_data.price > 10000:
        raise BusinessLogicException(
            detail="Product price cannot exceed $10,000",
            error_code="PRICE_TOO_HIGH",
            context={"max_price": 10000, "provided_price": product_data.price},
        )

    ***REMOVED*** Create new product
    new_id = max((p.id for p in products_db), default=0) + 1
    new_product = Product(
        id=new_id,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        in_stock=product_data.in_stock,
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    products_db.append(new_product)

    return create_success_response(
        message="Product created successfully",
        data=new_product.dict(),
    )


***REMOVED*** Create application
def create_advanced_app():
    """Create the advanced FastAPI application."""
    ***REMOVED*** Configuration
    settings = AdvancedAppConfig()

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
        settings,
        options=options,
        title="Advanced Fast Core Example API",
        description="A comprehensive example showing all Fast Core features",
        version="1.0.0",
    )

    ***REMOVED*** Add health checks
    health_checks = [
        HealthCheck(name="database", check_func=check_database),
        HealthCheck(name="cache", check_func=check_cache),
        HealthCheck(name="external_service", check_func=check_external_service),
    ]
    setup_health_checks(app, health_checks)

    ***REMOVED*** Include routers
    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(admin_router)

    return app


***REMOVED*** Create the app
app = create_advanced_app()


if __name__ == "__main__":
    uvicorn.run(
        "advanced_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

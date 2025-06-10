***REMOVED*** Services Module

The services module contains the core business logic for the Auth API. It provides a clean abstraction layer between the API routes and the underlying database operations, implementing domain-specific functionality for authentication and health monitoring.

***REMOVED******REMOVED*** Overview

The services in this module handle:

- **Authentication Operations**: User registration, login, token management
- **Health Monitoring**: Database health checks and system monitoring
- **Business Logic**: Centralized logic that can be reused across routes and CLI commands
- **Data Validation**: Ensuring data integrity and security

***REMOVED******REMOVED*** Services

***REMOVED******REMOVED******REMOVED*** AuthService (`auth_service.py`)

The primary service for handling all authentication-related operations.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **User Registration**: Secure user account creation with validation
- **Authentication**: Login verification with multiple input formats
- **Token Management**: JWT token generation, validation, and refresh
- **Password Security**: Bcrypt hashing with configurable rounds
- **Rate Limiting**: Protection against brute force attacks
- **Session Management**: User session tracking and timeout handling

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Methods

```python
***REMOVED*** User Registration
async def register_user(user_data: UserRegistrationSchema) -> User
async def create_user(email: str, username: str, password: str) -> User

***REMOVED*** Authentication
async def authenticate_user(email: str, password: str) -> Optional[User]
async def login_user(credentials: LoginCredentials) -> LoginResponse

***REMOVED*** Token Operations
def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str
def create_refresh_token(user_id: int) -> str
async def verify_token(token: str) -> Optional[User]
async def refresh_access_token(refresh_token: str) -> TokenResponse

***REMOVED*** User Management
async def get_user_by_email(email: str) -> Optional[User]
async def get_user_by_id(user_id: int) -> Optional[User]
async def update_user_last_login(user_id: int) -> None
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage Examples

```python
from auth_api.services.auth_service import auth_service

***REMOVED*** Register a new user
user_data = UserRegistrationSchema(
    email="user@example.com",
    username="testuser",
    password="secure123",
    password_confirm="secure123"
)
user = await auth_service.register_user(user_data)

***REMOVED*** Authenticate user
credentials = LoginCredentials(email="user@example.com", password="secure123")
login_response = await auth_service.login_user(credentials)

***REMOVED*** Verify a token
user = await auth_service.verify_token("jwt-token-here")
if user:
    print(f"Token valid for user: {user.email}")
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Configuration

The AuthService respects these environment variables:

- `JWT_SECRET`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime
- `PASSWORD_HASH_ROUNDS`: Bcrypt rounds for password hashing
- `MAX_LOGIN_ATTEMPTS`: Maximum failed login attempts
- `LOGIN_LOCKOUT_DURATION_MINUTES`: Lockout duration after max attempts

***REMOVED******REMOVED******REMOVED*** HealthService (`health_service.py`)

Comprehensive health monitoring service for the Auth API and its dependencies.

***REMOVED******REMOVED******REMOVED******REMOVED*** Key Features

- **Database Health Checks**: PostgreSQL connectivity and performance monitoring
- **Response Time Tracking**: Measures database query performance
- **Multiple Check Types**: Supports different health check granularities
- **Error Handling**: Graceful degradation when services are unavailable
- **Structured Results**: Consistent health check response format

***REMOVED******REMOVED******REMOVED******REMOVED*** Main Methods

```python
***REMOVED*** Comprehensive health check
async def check_all() -> HealthCheckResult

***REMOVED*** Database-specific health check
async def check_postgres() -> Dict[str, Any]

***REMOVED*** Quick health status
def get_basic_health() -> Dict[str, str]
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Usage Examples

```python
from auth_api.services.health_service import health_service

***REMOVED*** Full health check
health_result = await health_service.check_all()
print(f"Overall status: {health_result.status}")
print(f"Database healthy: {health_result.database['healthy']}")

***REMOVED*** Database-only check
db_health = await health_service.check_postgres()
print(f"DB response time: {db_health['response_time_ms']}ms")
```

***REMOVED******REMOVED******REMOVED******REMOVED*** HealthCheckResult Structure

```python
@dataclass
class HealthCheckResult:
    status: str                    ***REMOVED*** "healthy" or "unhealthy"
    timestamp: datetime
    response_time_ms: float
    database: Dict[str, Any]       ***REMOVED*** Database health details
    version: str                   ***REMOVED*** Service version
    environment: str               ***REMOVED*** Current environment
```

***REMOVED******REMOVED*** Service Architecture

***REMOVED******REMOVED******REMOVED*** Dependency Injection

Services are designed to be easily testable and configurable:

```python
***REMOVED*** Services can be instantiated with custom configurations
auth_service = AuthService(config=custom_config)
health_service = HealthService(database=custom_db)
```

***REMOVED******REMOVED******REMOVED*** Global Instances

For convenience, global service instances are provided:

```python
***REMOVED*** Available as singleton instances
from auth_api.services import auth_service, health_service

***REMOVED*** These instances use the default application configuration
user = await auth_service.authenticate_user(email, password)
health = await health_service.check_all()
```

***REMOVED******REMOVED******REMOVED*** Error Handling

Services implement consistent error handling patterns:

- **Authentication Errors**: Specific exceptions for different failure types
- **Database Errors**: Graceful handling of connection issues
- **Validation Errors**: Clear error messages for invalid input
- **Rate Limiting**: Proper handling of rate limit violations

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests

Each service has comprehensive unit tests:

```bash
***REMOVED*** Run service tests
hatch run test tests/test_services/

***REMOVED*** Run specific service tests
hatch run test tests/test_services/test_auth_service.py
hatch run test tests/test_services/test_health_service.py
```

***REMOVED******REMOVED******REMOVED*** Mocking Dependencies

Services are designed for easy mocking in tests:

```python
***REMOVED*** Mock database for testing
@pytest.fixture
def mock_auth_service():
    with patch('auth_api.services.auth_service.database') as mock_db:
        yield AuthService(database=mock_db)
```

***REMOVED******REMOVED*** Best Practices

***REMOVED******REMOVED******REMOVED*** Service Configuration

1. **Environment Variables**: Always use environment-based configuration
2. **Default Values**: Provide sensible defaults for all configuration
3. **Validation**: Validate configuration at service startup

***REMOVED******REMOVED******REMOVED*** Performance

1. **Database Connections**: Use connection pooling for database operations
2. **Caching**: Cache frequently accessed data (user sessions, tokens)
3. **Async Operations**: Use async/await for all I/O operations

***REMOVED******REMOVED******REMOVED*** Security

1. **Password Hashing**: Always use bcrypt with appropriate rounds
2. **Token Security**: Use strong secrets and appropriate expiration times
3. **Input Validation**: Validate all inputs before processing
4. **Rate Limiting**: Implement rate limiting for authentication endpoints

***REMOVED******REMOVED******REMOVED*** Error Handling

1. **Specific Exceptions**: Use domain-specific exception types
2. **Logging**: Log errors with appropriate detail levels
3. **User Messages**: Provide clear error messages without exposing internals
4. **Graceful Degradation**: Handle service unavailability gracefully

***REMOVED******REMOVED*** Contributing

When adding new services:

1. **Follow Patterns**: Use existing services as templates
2. **Add Tests**: Include comprehensive unit and integration tests
3. **Document**: Add docstrings and update this README
4. **Configuration**: Support environment-based configuration
5. **Error Handling**: Implement consistent error handling patterns

***REMOVED******REMOVED*** Dependencies

Services depend on:

- **Database**: SQLModel/SQLAlchemy for data access
- **Authentication**: JWT libraries for token operations
- **Validation**: Pydantic for data validation
- **Configuration**: Environment variable management
- **Logging**: Structured logging for monitoring

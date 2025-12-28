"""Type definitions for cache warming system."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WarmingStatus(Enum):
    """Status of warming operations."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WarmingStrategy(Enum):
    """Available warming strategies."""

    METRICS_DRIVEN = "metrics_driven"
    POPULAR_CONTENT = "popular_content"
    USER_SPECIFIC = "user_specific"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


@dataclass
class WarmingTarget:
    """Represents a target for cache warming."""

    function_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0
    estimated_benefit: float = 0.0
    ttl: int | None = None
    strategy: WarmingStrategy | None = None

    def __post_init__(self) -> None:
        """Validate warming target."""
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")


@dataclass
class WarmingResult:
    """Result of a warming operation."""

    target: WarmingTarget
    status: WarmingStatus
    start_time: datetime
    end_time: datetime | None = None
    error: str | None = None
    cache_key: str | None = None
    execution_time_ms: float | None = None

    @property
    def duration_ms(self) -> float | None:
        """Calculate duration in milliseconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    @property
    def success(self) -> bool:
        """Check if warming was successful."""
        return self.status == WarmingStatus.COMPLETED


@dataclass
class WarmingBatch:
    """A batch of warming operations."""

    targets: list[WarmingTarget]
    strategy: WarmingStrategy
    max_concurrent: int = 5
    timeout_seconds: int = 300
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Validate batch parameters."""
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class WarmingStats:
    """Statistics for warming operations."""

    total_targets: int = 0
    successful_targets: int = 0
    failed_targets: int = 0
    total_execution_time_ms: float = 0.0
    average_execution_time_ms: float = 0.0
    cache_hit_rate_improvement: float = 0.0
    strategy_breakdown: dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_targets == 0:
            return 0.0
        return self.successful_targets / self.total_targets

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return 1.0 - self.success_rate


@dataclass
class WarmingConfig:
    """Configuration for warming operations."""

    ***REMOVED*** Execution limits
    max_concurrent_operations: int = 5
    max_warming_duration_minutes: int = 30
    max_items_per_strategy: int = 100
    operation_timeout_seconds: int = 60

    ***REMOVED*** Resource limits
    max_memory_usage_mb: int = 500
    max_cpu_usage_percent: float = 50.0

    ***REMOVED*** Strategy configuration
    enable_metrics_driven: bool = True
    enable_popular_content: bool = True
    enable_user_specific: bool = False
    enable_scheduled: bool = True

    ***REMOVED*** Strategy weights (for priority calculation)
    metrics_driven_weight: float = 1.0
    popular_content_weight: float = 0.8
    user_specific_weight: float = 0.6
    scheduled_weight: float = 0.7

    ***REMOVED*** Thresholds for metrics-driven warming
    min_miss_rate_threshold: float = 0.3
    min_avg_miss_time_ms: float = 100.0
    min_total_calls: int = 10

    ***REMOVED*** Popular content configuration
    popular_content_refresh_hours: int = 6
    max_popular_items_per_type: int = 20

    ***REMOVED*** User-specific configuration
    max_users_per_batch: int = 50
    user_preference_weight: float = 1.2
    recommendation_confidence_threshold: float = 0.6

    ***REMOVED*** Scheduled warming configuration
    enable_peak_hour_warming: bool = True
    enable_off_peak_preparation: bool = True
    peak_hour_multiplier: float = 1.5
    seasonal_content_weight: float = 0.9

    ***REMOVED*** Scheduling
    enable_automatic_warming: bool = True
    warming_schedules: dict[str, str] = field(
        default_factory=lambda: {
            "morning_warmup": "0 7 * * *",
            "evening_warmup": "0 17 * * *",
            "weekend_prep": "0 18 * * 5",
        }
    )

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_concurrent_operations <= 0:
            raise ValueError("max_concurrent_operations must be positive")
        if self.max_warming_duration_minutes <= 0:
            raise ValueError("max_warming_duration_minutes must be positive")


***REMOVED*** Type aliases for warming functions
WarmingFunction = Callable[..., Awaitable[Any]]
WarmingCallback = Callable[[WarmingResult], Awaitable[None]]

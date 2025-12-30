"""Scheduled warming strategy."""

from datetime import datetime, time
from enum import Enum
from typing import Any

import structlog

from cache.warming.types import WarmingConfig, WarmingStrategy, WarmingTarget

from .base import BaseWarmingStrategy

logger = structlog.get_logger(__name__)


class ScheduleType(Enum):
    """Types of scheduled warming."""

    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"
    DAILY = "daily"
    WEEKLY = "weekly"
    SEASONAL = "seasonal"
    EVENT_BASED = "event_based"


class ScheduledStrategy(BaseWarmingStrategy):
    """Warming strategy based on time-based patterns and schedules."""

    def __init__(self, config: WarmingConfig, schedule_config: dict[str, Any] | None = None):
        """Initialize scheduled strategy.

        Args:
            config: Warming configuration
            schedule_config: Schedule-specific configuration
        """
        super().__init__(config)
        self.strategy_type = WarmingStrategy.SCHEDULED
        self.schedule_config = schedule_config or self._get_default_schedule_config()

    def _get_default_schedule_config(self) -> dict[str, Any]:
        """Get default schedule configuration.

        Returns:
            Default schedule configuration
        """
        return {
            "peak_hours": {
                "weekday": [(18, 23)],  # 6 PM - 11 PM
                "weekend": [(12, 24)],  # 12 PM - 12 AM
            },
            "off_peak_hours": {
                "weekday": [(2, 6)],  # 2 AM - 6 AM
                "weekend": [(3, 8)],  # 3 AM - 8 AM
            },
            "daily_schedules": {
                "morning_prep": time(6, 0),  # 6 AM
                "evening_prep": time(17, 0),  # 5 PM
                "night_cleanup": time(1, 0),  # 1 AM
            },
            "weekly_schedules": {
                "monday": ["new_releases", "trending"],
                "friday": ["weekend_popular", "family_content"],
                "sunday": ["weekly_recap", "coming_soon"],
            },
            "seasonal_events": {
                "holidays": ["christmas", "thanksgiving", "halloween"],
                "award_seasons": ["oscars", "golden_globes", "emmys"],
                "summer_blockbusters": ["may", "june", "july", "august"],
            },
        }

    async def identify_targets(
        self, limit: int | None = None, context: dict[str, Any] | None = None
    ) -> list[WarmingTarget]:
        """Identify warming targets based on current time and schedule.

        Args:
            limit: Maximum number of targets to return
            context: Context with time information

        Returns:
            List of warming targets for scheduled content
        """
        current_time = context.get("current_time", datetime.now()) if context else datetime.now()

        targets = []

        # Determine current schedule context
        schedule_context = self._analyze_schedule_context(current_time)

        # Generate targets based on schedule context
        targets.extend(await self._create_peak_hour_targets(current_time, schedule_context))
        targets.extend(await self._create_daily_schedule_targets(current_time, schedule_context))
        targets.extend(await self._create_weekly_schedule_targets(current_time, schedule_context))
        targets.extend(await self._create_seasonal_targets(current_time, schedule_context))

        # Sort by priority and apply limit
        targets.sort(key=lambda t: t.priority, reverse=True)
        if limit:
            targets = targets[:limit]

        logger.info(f"Identified {len(targets)} scheduled targets for warming at {current_time}")
        return targets

    def _analyze_schedule_context(self, current_time: datetime) -> dict[str, Any]:
        """Analyze current time to determine schedule context.

        Args:
            current_time: Current datetime

        Returns:
            Schedule context information
        """
        is_weekend = current_time.weekday() >= 5
        current_hour = current_time.hour
        day_name = current_time.strftime("%A").lower()
        month_name = current_time.strftime("%B").lower()

        # Determine if it's peak hours
        peak_ranges = self.schedule_config["peak_hours"]["weekend" if is_weekend else "weekday"]
        is_peak_hour = any(start <= current_hour <= end for start, end in peak_ranges)

        # Determine if it's off-peak hours
        off_peak_ranges = self.schedule_config["off_peak_hours"][
            "weekend" if is_weekend else "weekday"
        ]
        is_off_peak = any(start <= current_hour <= end for start, end in off_peak_ranges)

        return {
            "is_weekend": is_weekend,
            "is_peak_hour": is_peak_hour,
            "is_off_peak": is_off_peak,
            "current_hour": current_hour,
            "day_name": day_name,
            "month_name": month_name,
            "time_of_day": self._get_time_of_day(current_hour),
        }

    def _get_time_of_day(self, hour: int) -> str:
        """Get time of day category.

        Args:
            hour: Hour of day (0-23)

        Returns:
            Time of day category
        """
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    async def _create_peak_hour_targets(
        self, current_time: datetime, schedule_context: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create targets for peak hour preparation.

        Args:
            current_time: Current datetime
            schedule_context: Schedule context

        Returns:
            List of peak hour warming targets
        """
        targets = []

        if schedule_context["is_peak_hour"]:
            # During peak hours, warm high-traffic content
            priority_base = self.calculate_priority(
                {
                    "schedule_type": ScheduleType.PEAK_HOURS.value,
                    "urgency": "high",
                    "time_context": schedule_context,
                }
            )

            # Popular movie screens
            popular_movie_ids = [1, 2, 3, 254, 550]  # Would come from analytics
            for movie_id in popular_movie_ids:
                targets.append(
                    self.create_warming_target(
                        function_name="get_movie_screen_data",
                        parameters={"movie_id": movie_id, "user_id": None},
                        priority=priority_base * 1.2,
                        estimated_benefit=200.0,
                    )
                )

            # Homepage and trending content
            targets.append(
                self.create_warming_target(
                    function_name="get_homepage_data",
                    parameters={},
                    priority=priority_base * 1.5,
                    estimated_benefit=300.0,
                )
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_trending_movies",
                    parameters={"page": 1, "limit": 20},
                    priority=priority_base * 1.3,
                    estimated_benefit=250.0,
                )
            )

        elif schedule_context["is_off_peak"]:
            # During off-peak, prepare for upcoming peak
            priority_base = self.calculate_priority(
                {
                    "schedule_type": ScheduleType.OFF_PEAK.value,
                    "urgency": "medium",
                    "time_context": schedule_context,
                }
            )

            # Pre-warm content for next peak period
            targets.append(
                self.create_warming_target(
                    function_name="get_homepage_data",
                    parameters={},
                    priority=priority_base,
                    estimated_benefit=150.0,
                )
            )

        return targets

    async def _create_daily_schedule_targets(
        self, current_time: datetime, schedule_context: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create targets based on daily schedules.

        Args:
            current_time: Current datetime
            schedule_context: Schedule context

        Returns:
            List of daily schedule warming targets
        """
        targets = []
        current_time_only = current_time.time()

        priority_base = self.calculate_priority(
            {
                "schedule_type": ScheduleType.DAILY.value,
                "urgency": "medium",
                "time_context": schedule_context,
            }
        )

        # Morning preparation (6 AM)
        morning_prep = self.schedule_config["daily_schedules"]["morning_prep"]
        if self._is_near_time(current_time_only, morning_prep, minutes=30):
            # Warm content for morning viewers
            targets.append(
                self.create_warming_target(
                    function_name="get_morning_recommendations",
                    parameters={},
                    priority=priority_base,
                    estimated_benefit=120.0,
                )
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_news_and_updates",
                    parameters={},
                    priority=priority_base * 0.8,
                    estimated_benefit=100.0,
                )
            )

        # Evening preparation (5 PM)
        evening_prep = self.schedule_config["daily_schedules"]["evening_prep"]
        if self._is_near_time(current_time_only, evening_prep, minutes=60):
            # Warm content for evening prime time
            targets.append(
                self.create_warming_target(
                    function_name="get_prime_time_content",
                    parameters={},
                    priority=priority_base * 1.2,
                    estimated_benefit=180.0,
                )
            )

            targets.append(
                self.create_warming_target(
                    function_name="get_family_friendly_content",
                    parameters={},
                    priority=priority_base,
                    estimated_benefit=140.0,
                )
            )

        return targets

    async def _create_weekly_schedule_targets(
        self, current_time: datetime, schedule_context: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create targets based on weekly schedules.

        Args:
            current_time: Current datetime
            schedule_context: Schedule context

        Returns:
            List of weekly schedule warming targets
        """
        targets = []
        day_name = schedule_context["day_name"]

        if day_name in self.schedule_config["weekly_schedules"]:
            content_types = self.schedule_config["weekly_schedules"][day_name]

            priority_base = self.calculate_priority(
                {
                    "schedule_type": ScheduleType.WEEKLY.value,
                    "urgency": "medium",
                    "time_context": schedule_context,
                }
            )

            for content_type in content_types:
                if content_type == "new_releases":
                    targets.append(
                        self.create_warming_target(
                            function_name="get_new_releases",
                            parameters={"page": 1, "limit": 20},
                            priority=priority_base,
                            estimated_benefit=160.0,
                        )
                    )

                elif content_type == "trending":
                    targets.append(
                        self.create_warming_target(
                            function_name="get_trending_movies",
                            parameters={"page": 1, "limit": 20},
                            priority=priority_base,
                            estimated_benefit=140.0,
                        )
                    )

                elif content_type == "weekend_popular":
                    targets.append(
                        self.create_warming_target(
                            function_name="get_weekend_popular",
                            parameters={},
                            priority=priority_base * 1.1,
                            estimated_benefit=170.0,
                        )
                    )

        return targets

    async def _create_seasonal_targets(
        self, current_time: datetime, schedule_context: dict[str, Any]
    ) -> list[WarmingTarget]:
        """Create targets based on seasonal events.

        Args:
            current_time: Current datetime
            schedule_context: Schedule context

        Returns:
            List of seasonal warming targets
        """
        targets = []
        month_name = schedule_context["month_name"]

        priority_base = self.calculate_priority(
            {
                "schedule_type": ScheduleType.SEASONAL.value,
                "urgency": "low",
                "time_context": schedule_context,
            }
        )

        # Summer blockbusters
        if month_name in self.schedule_config["seasonal_events"]["summer_blockbusters"]:
            targets.append(
                self.create_warming_target(
                    function_name="get_summer_blockbusters",
                    parameters={},
                    priority=priority_base,
                    estimated_benefit=130.0,
                )
            )

        # Holiday content
        if self._is_holiday_season(current_time):
            targets.append(
                self.create_warming_target(
                    function_name="get_holiday_movies",
                    parameters={},
                    priority=priority_base * 1.2,
                    estimated_benefit=150.0,
                )
            )

        return targets

    def _is_near_time(self, current_time: time, target_time: time, minutes: int = 30) -> bool:
        """Check if current time is near target time.

        Args:
            current_time: Current time
            target_time: Target time
            minutes: Minutes tolerance

        Returns:
            True if within tolerance
        """
        current_minutes = current_time.hour * 60 + current_time.minute
        target_minutes = target_time.hour * 60 + target_time.minute

        return abs(current_minutes - target_minutes) <= minutes

    def _is_holiday_season(self, current_time: datetime) -> bool:
        """Check if current time is during holiday season.

        Args:
            current_time: Current datetime

        Returns:
            True if during holiday season
        """
        month = current_time.month
        day = current_time.day

        # Holiday seasons (simplified)
        holiday_periods = [
            (11, 20, 12, 31),  # Thanksgiving to New Year
            (10, 15, 11, 5),  # Halloween season
            (2, 1, 2, 20),  # Valentine's season
        ]

        for start_month, start_day, end_month, end_day in holiday_periods:
            if (
                (month == start_month and day >= start_day)
                or (month == end_month and day <= end_day)
                or (start_month < month < end_month)
            ):
                return True

        return False

    def calculate_priority(self, target_data: dict[str, Any]) -> float:
        """Calculate priority based on schedule type and urgency.

        Args:
            target_data: Schedule-specific target data

        Returns:
            Priority score
        """
        schedule_type = target_data.get("schedule_type", "unknown")
        urgency = target_data.get("urgency", "low")
        time_context = target_data.get("time_context", {})

        # Base priority from schedule type
        schedule_multipliers = {
            ScheduleType.PEAK_HOURS.value: 2.0,
            ScheduleType.OFF_PEAK.value: 1.5,
            ScheduleType.DAILY.value: 1.2,
            ScheduleType.WEEKLY.value: 1.0,
            ScheduleType.SEASONAL.value: 0.8,
            "unknown": 0.5,
        }

        base_priority = schedule_multipliers.get(schedule_type, 0.5)

        # Urgency multipliers
        urgency_multipliers = {"high": 1.5, "medium": 1.0, "low": 0.7}

        urgency_multiplier = urgency_multipliers.get(urgency, 1.0)

        # Time context boosts
        context_boost = 1.0
        if time_context.get("is_peak_hour"):
            context_boost *= 1.3
        if time_context.get("is_weekend"):
            context_boost *= 1.1

        return base_priority * urgency_multiplier * context_boost * self.config.scheduled_weight

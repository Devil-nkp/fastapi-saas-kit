"""
Quota enforcement — track and enforce usage limits per plan.
"""

from datetime import UTC, datetime, timedelta

import structlog
from fastapi import HTTPException

from ..auth.models import CurrentUser
from .config import get_plan_quota

logger = structlog.get_logger("saas_kit.quota")

USAGE_PERIOD_DAYS = 30


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _period_needs_reset(period_start: datetime | None) -> bool:
    """Check if the current usage period has expired."""
    if not period_start:
        return True
    if period_start.tzinfo is None:
        period_start = period_start.replace(tzinfo=UTC)
    return _utcnow() >= period_start + timedelta(days=USAGE_PERIOD_DAYS)


async def check_quota(
    user: CurrentUser,
    quota_type: str,
    current_usage: int,
) -> None:
    """Check if the user has remaining quota.

    Raises HTTP 402 if the quota is exceeded.

    Args:
        user: The authenticated user.
        quota_type: Type of quota to check (monthly_requests, team_members, etc.).
        current_usage: The user's current usage count.

    Raises:
        HTTPException: 402 if quota exceeded.
    """
    # Admins bypass quota checks
    if user.is_admin:
        logger.info("quota_bypassed_admin", user_id=user.id, quota_type=quota_type)
        return

    limit = get_plan_quota(user.plan, quota_type)

    # None means unlimited
    if limit is None:
        logger.info("quota_unlimited", user_id=user.id, plan=user.plan, quota_type=quota_type)
        return

    if current_usage >= limit:
        logger.info(
            "quota_exceeded",
            user_id=user.id,
            plan=user.plan,
            quota_type=quota_type,
            used=current_usage,
            limit=limit,
        )
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "message": f"You've reached the {quota_type} limit for your {user.plan.title()} plan.",
                "quota_type": quota_type,
                "used": current_usage,
                "limit": limit,
                "plan": user.plan,
                "upgrade_url": "/pricing",
            },
        )

    remaining = limit - current_usage
    logger.info(
        "quota_check_passed",
        user_id=user.id,
        plan=user.plan,
        quota_type=quota_type,
        used=current_usage,
        limit=limit,
        remaining=remaining,
    )


def get_usage_stats(
    plan: str,
    usage: dict[str, int],
) -> dict:
    """Get quota usage statistics for a user.

    Args:
        plan: The user's current plan.
        usage: Dict of quota_type -> current_usage.

    Returns:
        Dict with usage stats per quota type.
    """
    stats: dict[str, dict] = {}
    for quota_type, used in usage.items():
        limit = get_plan_quota(plan, quota_type)
        is_unlimited = limit is None
        stats[quota_type] = {
            "used": used,
            "limit": limit,
            "remaining": None if is_unlimited else max(0, limit - used),
            "is_unlimited": is_unlimited,
            "percentage_used": 0 if is_unlimited else round((used / max(limit, 1)) * 100, 1),
        }
    return stats


def should_reset_period(period_start: datetime | None) -> bool:
    """Check if the usage period needs to be reset.

    Call this at the start of quota-related operations to
    determine if the rolling window has expired.

    Args:
        period_start: When the current period started.

    Returns:
        True if the period should be reset.
    """
    return _period_needs_reset(period_start)

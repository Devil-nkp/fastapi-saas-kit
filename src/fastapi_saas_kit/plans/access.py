"""
Plan access helpers — plan hierarchy checks and feature gates.
"""

from fastapi import Depends, HTTPException

from ..auth.dependencies import get_current_user
from ..auth.models import CurrentUser
from .config import PLAN_HIERARCHY, has_feature


def require_feature(feature: str):
    """FastAPI dependency that gates access based on a plan feature.

    Usage:
        @router.get("/analytics")
        async def get_analytics(user: CurrentUser = Depends(require_feature("advanced_analytics"))):
            ...
    """

    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.is_admin:
            return user

        if not has_feature(user.plan, feature):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_not_available",
                    "message": f"The '{feature}' feature requires a higher plan.",
                    "feature": feature,
                    "current_plan": user.plan,
                    "upgrade_url": "/pricing",
                },
            )
        return user

    return dependency


def check_plan_access(user_plan: str, required_plan: str) -> bool:
    """Check if a user's plan meets the minimum requirement.

    Args:
        user_plan: The user's current plan.
        required_plan: The minimum required plan.

    Returns:
        True if user's plan level >= required plan level.
    """
    user_level = PLAN_HIERARCHY.get(user_plan, 0)
    required_level = PLAN_HIERARCHY.get(required_plan, 0)
    return user_level >= required_level

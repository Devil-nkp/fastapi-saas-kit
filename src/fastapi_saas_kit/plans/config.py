"""
Access tier configuration - defines available tiers, limits, and feature gates.
"""

# ── Plan Definitions ─────────────────────────────────────────
# Customize these to match your application's access model.
# Each tier defines quotas, feature flags, and display metadata.

PLAN_CONFIG: dict[str, dict] = {
    "free": {
        "display_name": "Free",
        "description": "Get started with basic features",
        "price_cents": 0,
        "price_display": "Free",
        "quotas": {
            "monthly_requests": 100,
            "team_members": 1,
            "projects": 3,
            "storage_mb": 100,
        },
        "features": {
            "api_access": True,
            "basic_analytics": True,
            "advanced_analytics": False,
            "priority_support": False,
            "custom_branding": False,
            "export_data": False,
            "webhooks": False,
            "sso": False,
        },
    },
    "pro": {
        "display_name": "Pro",
        "description": "For growing teams and professionals",
        "price_cents": 2900,
        "price_display": "$29/month",
        "quotas": {
            "monthly_requests": 5000,
            "team_members": 10,
            "projects": 25,
            "storage_mb": 5000,
        },
        "features": {
            "api_access": True,
            "basic_analytics": True,
            "advanced_analytics": True,
            "priority_support": True,
            "custom_branding": False,
            "export_data": True,
            "webhooks": True,
            "sso": False,
        },
    },
    "business": {
        "display_name": "Advanced",
        "description": "For larger teams and advanced deployments",
        "price_cents": 9900,
        "price_display": "$99/month",
        "quotas": {
            "monthly_requests": None,  # Unlimited
            "team_members": 100,
            "projects": None,  # Unlimited
            "storage_mb": 50000,
        },
        "features": {
            "api_access": True,
            "basic_analytics": True,
            "advanced_analytics": True,
            "priority_support": True,
            "custom_branding": True,
            "export_data": True,
            "webhooks": True,
            "sso": True,
        },
    },
}

VALID_PLANS = set(PLAN_CONFIG.keys())
PLAN_HIERARCHY = {"free": 0, "pro": 1, "business": 2}


def get_plan_config(plan: str) -> dict:
    """Return a safe copy of the plan configuration.

    Falls back to the free plan if the given plan is unknown.

    Args:
        plan: Internal access tier key.

    Returns:
        Access tier configuration dictionary.
    """
    selected = (plan or "free").lower().strip()
    return dict(PLAN_CONFIG.get(selected, PLAN_CONFIG["free"]))


def is_valid_plan(plan: str) -> bool:
    """Check if the plan name is recognized."""
    return (plan or "").lower().strip() in VALID_PLANS


def can_access_plan(user_plan: str, required_plan: str) -> bool:
    """Check if a user's plan meets or exceeds the required plan level.

    Args:
        user_plan: The user's current plan.
        required_plan: The minimum required plan.

    Returns:
        True if user_plan >= required_plan in the hierarchy.
    """
    user_level = PLAN_HIERARCHY.get((user_plan or "free").lower().strip(), 0)
    required_level = PLAN_HIERARCHY.get((required_plan or "free").lower().strip(), 0)
    return user_level >= required_level


def highest_plan(plans: list[str]) -> str:
    """Return the highest-tier plan from a list.

    Args:
        plans: List of plan names.

    Returns:
        The highest plan name, defaulting to 'free'.
    """
    valid = [p for p in plans if p in VALID_PLANS]
    if not valid:
        return "free"
    return max(valid, key=lambda p: PLAN_HIERARCHY.get(p, 0))


def get_plan_quota(plan: str, quota_type: str) -> int | None:
    """Get a specific quota value for a plan.

    Args:
        plan: Plan name.
        quota_type: Quota key (monthly_requests, team_members, etc.).

    Returns:
        The quota limit, or None if unlimited.
    """
    config = get_plan_config(plan)
    return config.get("quotas", {}).get(quota_type)


def has_feature(plan: str, feature: str) -> bool:
    """Check if a plan includes a specific feature.

    Args:
        plan: Plan name.
        feature: Feature key (api_access, advanced_analytics, etc.).

    Returns:
        True if the feature is enabled for the plan.
    """
    config = get_plan_config(plan)
    return config.get("features", {}).get(feature, False)

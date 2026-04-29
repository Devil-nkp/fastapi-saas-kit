"""
Tests for plan configuration, quota enforcement, and feature gates.
"""

from datetime import UTC, datetime, timedelta

import pytest


class TestPlanConfig:
    """Test plan configuration and hierarchy."""

    def test_valid_plans(self):
        from fastapi_saas_kit.plans.config import VALID_PLANS
        assert "free" in VALID_PLANS
        assert "pro" in VALID_PLANS
        assert "business" in VALID_PLANS

    def test_plan_hierarchy(self):
        from fastapi_saas_kit.plans.config import can_access_plan
        assert can_access_plan("business", "free")
        assert can_access_plan("business", "pro")
        assert can_access_plan("business", "business")
        assert can_access_plan("pro", "free")
        assert can_access_plan("pro", "pro")
        assert not can_access_plan("pro", "business")
        assert not can_access_plan("free", "pro")
        assert not can_access_plan("free", "business")

    def test_highest_plan(self):
        from fastapi_saas_kit.plans.config import highest_plan
        assert highest_plan(["free", "pro"]) == "pro"
        assert highest_plan(["free", "pro", "business"]) == "business"
        assert highest_plan(["free"]) == "free"
        assert highest_plan([]) == "free"

    def test_get_plan_config_fallback(self):
        from fastapi_saas_kit.plans.config import get_plan_config
        config = get_plan_config("nonexistent")
        assert config["display_name"] == "Free"

    def test_is_valid_plan(self):
        from fastapi_saas_kit.plans.config import is_valid_plan
        assert is_valid_plan("free")
        assert is_valid_plan("pro")
        assert is_valid_plan("business")
        assert not is_valid_plan("enterprise")
        assert not is_valid_plan("")

    def test_plan_quotas(self):
        from fastapi_saas_kit.plans.config import get_plan_quota
        assert get_plan_quota("free", "monthly_requests") == 100
        assert get_plan_quota("pro", "monthly_requests") == 5000
        assert get_plan_quota("business", "monthly_requests") is None  # Unlimited
        assert get_plan_quota("free", "team_members") == 1

    def test_plan_features(self):
        from fastapi_saas_kit.plans.config import has_feature
        assert has_feature("free", "api_access")
        assert not has_feature("free", "advanced_analytics")
        assert has_feature("pro", "advanced_analytics")
        assert has_feature("business", "sso")
        assert not has_feature("free", "sso")


class TestQuota:
    """Test quota enforcement."""

    @pytest.mark.asyncio
    async def test_quota_passes_under_limit(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole
        from fastapi_saas_kit.plans.quota import check_quota

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.USER, plan="free")
        # Should not raise — 50 < 100
        await check_quota(user, "monthly_requests", 50)

    @pytest.mark.asyncio
    async def test_quota_fails_over_limit(self):
        from fastapi import HTTPException

        from fastapi_saas_kit.auth.models import CurrentUser, UserRole
        from fastapi_saas_kit.plans.quota import check_quota

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.USER, plan="free")
        with pytest.raises(HTTPException) as exc_info:
            await check_quota(user, "monthly_requests", 100)
        assert exc_info.value.status_code == 402

    @pytest.mark.asyncio
    async def test_admin_bypasses_quota(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole
        from fastapi_saas_kit.plans.quota import check_quota

        admin = CurrentUser(id="1", email="admin@test.com", role=UserRole.MAIN_ADMIN, plan="free")
        # Admin should not be rate limited even if over quota
        await check_quota(admin, "monthly_requests", 9999)

    @pytest.mark.asyncio
    async def test_unlimited_quota_passes(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole
        from fastapi_saas_kit.plans.quota import check_quota

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.USER, plan="business")
        # Highest configured tier has unlimited monthly_requests
        await check_quota(user, "monthly_requests", 999999)

    def test_usage_stats(self):
        from fastapi_saas_kit.plans.quota import get_usage_stats

        stats = get_usage_stats("free", {"monthly_requests": 50, "team_members": 1})
        assert stats["monthly_requests"]["used"] == 50
        assert stats["monthly_requests"]["limit"] == 100
        assert stats["monthly_requests"]["remaining"] == 50
        assert stats["monthly_requests"]["percentage_used"] == 50.0

    def test_period_reset_check(self):
        from fastapi_saas_kit.plans.quota import should_reset_period

        assert should_reset_period(None) is True
        assert should_reset_period(datetime.now(UTC) - timedelta(days=31)) is True
        assert should_reset_period(datetime.now(UTC) - timedelta(days=1)) is False

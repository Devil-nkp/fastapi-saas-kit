"""
Tests for rate limiter behavior.
"""

import pytest

from fastapi_saas_kit.middleware.rate_limiter import (
    _memory_rate_check,
    clear_rate_limit_store,
    rate_limit_check,
)


@pytest.fixture(autouse=True)
def clean_rate_limits():
    """Clear rate limit store before each test."""
    clear_rate_limit_store()
    yield
    clear_rate_limit_store()


class TestMemoryRateLimiter:
    """Test in-memory sliding window rate limiter."""

    def test_allows_under_limit(self):
        """Requests under the limit should be allowed."""
        for _i in range(5):
            assert _memory_rate_check("test:key", 10, 60) is True

    def test_blocks_over_limit(self):
        """Requests over the limit should be blocked."""
        for _i in range(10):
            _memory_rate_check("test:key", 10, 60)
        assert _memory_rate_check("test:key", 10, 60) is False

    def test_different_keys_independent(self):
        """Different keys should have independent counters."""
        for _i in range(10):
            _memory_rate_check("key:a", 10, 60)
        # key:a is at limit
        assert _memory_rate_check("key:a", 10, 60) is False
        # key:b should still have capacity
        assert _memory_rate_check("key:b", 10, 60) is True

    def test_exact_limit_blocks(self):
        """Reaching exactly the limit should block the next request."""
        for _i in range(5):
            assert _memory_rate_check("exact", 5, 60) is True
        assert _memory_rate_check("exact", 5, 60) is False

    def test_clear_resets_store(self):
        """Clearing the store should reset all counters."""
        for _i in range(5):
            _memory_rate_check("test:clear", 5, 60)
        assert _memory_rate_check("test:clear", 5, 60) is False
        clear_rate_limit_store()
        assert _memory_rate_check("test:clear", 5, 60) is True


class TestAsyncRateLimit:
    """Test async rate limit check wrapper."""

    @pytest.mark.asyncio
    async def test_async_check_allows(self):
        """Async wrapper should pass through to memory check."""
        result = await rate_limit_check("async:test", 10, 60)
        assert result is True

    @pytest.mark.asyncio
    async def test_async_check_blocks(self):
        """Async wrapper should block when limit reached."""
        for _i in range(10):
            await rate_limit_check("async:block", 10, 60)
        result = await rate_limit_check("async:block", 10, 60)
        assert result is False

"""
Mock auth provider — for development and testing.
"""

from .interfaces import AuthProvider
from .models import CurrentUser, UserRole

# Pre-configured mock users for development and testing
MOCK_USERS: dict[str, CurrentUser] = {
    "user-001": CurrentUser(
        id="user-001",
        email="user@example.com",
        role=UserRole.USER,
        plan="free",
        organization_id="org-001",
    ),
    "user-002": CurrentUser(
        id="user-002",
        email="pro@example.com",
        role=UserRole.USER,
        plan="pro",
        organization_id="org-001",
    ),
    "org-admin-001": CurrentUser(
        id="org-admin-001",
        email="orgadmin@example.com",
        role=UserRole.ORG_ADMIN,
        plan="business",
        organization_id="org-001",
    ),
    "main-admin-001": CurrentUser(
        id="main-admin-001",
        email="admin@example.com",
        role=UserRole.MAIN_ADMIN,
        plan="business",
        organization_id=None,
    ),
}


class MockAuthProvider(AuthProvider):
    """Mock authentication provider for development and testing.

    Accepts tokens in the format 'mock-{user_id}' and returns
    pre-configured mock users. Any unknown token returns the
    default free-tier user.

    Usage:
        # In your tests or dev setup:
        provider = MockAuthProvider()
        user = await provider.verify_token("mock-user-001")
        assert user.email == "user@example.com"

        # Add custom users:
        provider = MockAuthProvider(extra_users={
            "custom-001": CurrentUser(id="custom-001", email="custom@test.com")
        })
    """

    def __init__(self, extra_users: dict[str, CurrentUser] | None = None):
        self._users = {**MOCK_USERS}
        if extra_users:
            self._users.update(extra_users)

    async def verify_token(self, token: str) -> CurrentUser | None:
        """Verify a mock token.

        Accepts formats:
        - 'mock-{user_id}' — returns the matching mock user
        - Any other non-empty string — returns the default free user
        - Empty string — returns None (unauthorized)
        """
        if not token:
            return None

        if token.startswith("mock-"):
            user_id = token[5:]  # strip 'mock-' prefix
            return self._users.get(user_id)

        # Any valid-looking token returns the default user
        return self._users.get("user-001")

    async def get_user_by_id(self, user_id: str) -> CurrentUser | None:
        """Fetch a mock user by ID."""
        return self._users.get(user_id)

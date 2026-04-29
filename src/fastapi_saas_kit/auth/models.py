"""
Auth models — user context and role definitions.
"""

from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    """Supported user roles in the SaaS platform."""

    USER = "user"
    ORG_ADMIN = "org_admin"
    MAIN_ADMIN = "main_admin"


class CurrentUser(BaseModel):
    """User context object attached to authenticated requests.

    This is the primary identity object used throughout the application.
    It is resolved by the auth provider and injected via FastAPI dependencies.
    """

    id: str
    email: str
    role: UserRole = UserRole.USER
    plan: str = "free"
    organization_id: str | None = None
    is_active: bool = True

    @property
    def is_admin(self) -> bool:
        """Check if user has main admin privileges."""
        return self.role == UserRole.MAIN_ADMIN

    @property
    def is_org_admin(self) -> bool:
        """Check if user is an organization admin."""
        return self.role in (UserRole.ORG_ADMIN, UserRole.MAIN_ADMIN)

    def has_role(self, minimum_role: UserRole) -> bool:
        """Check if user meets the minimum role requirement."""
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.ORG_ADMIN: 1,
            UserRole.MAIN_ADMIN: 2,
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(minimum_role, 0)


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str
    email: str
    role: str = "user"
    plan: str = "free"
    organization_id: str | None = None
    exp: int | None = None
    iat: int | None = None

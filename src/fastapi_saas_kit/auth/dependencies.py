"""
Auth dependencies - FastAPI dependency injection for authentication and RBAC.
"""

import structlog
from fastapi import Depends, HTTPException, Request

from ..config import get_settings
from .interfaces import AuthProvider
from .jwt import decode_access_token
from .mock import MockAuthProvider
from .models import CurrentUser, UserRole

logger = structlog.get_logger("saas_kit.auth")

# Module-level auth provider instance (configured during app initialization)
_auth_provider: AuthProvider | None = None


def configure_auth(provider: AuthProvider) -> None:
    """Configure the global auth provider.

    Call this during app initialization to set the authentication provider.

    Args:
        provider: An implementation of AuthProvider.
    """
    global _auth_provider
    _auth_provider = provider
    logger.info("auth_provider_configured", provider=type(provider).__name__)


def get_auth_provider() -> AuthProvider:
    """Get the configured auth provider, defaulting to MockAuthProvider."""
    if _auth_provider is None:
        return MockAuthProvider()
    return _auth_provider


async def get_current_user(request: Request) -> CurrentUser:
    """Extract and verify the user from the Authorization header.

    This is the primary authentication dependency. Inject it into
    any route that requires an authenticated user:

        @router.get("/profile")
        async def get_profile(user: CurrentUser = Depends(get_current_user)):
            return {"email": user.email, "plan": user.plan}
    """
    # Extract token from Authorization header
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ", 1)[1]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated. Please provide a valid token.")

    provider = get_auth_provider()

    # Try provider-based auth first
    user = await provider.verify_token(token)
    if user:
        return user

    # Fallback: try JWT decode for jwt-based auth
    settings = get_settings()
    if settings.AUTH_PROVIDER == "jwt":
        payload = decode_access_token(token)
        if payload:
            return CurrentUser(
                id=payload.sub,
                email=payload.email,
                role=UserRole(payload.role),
                plan=payload.plan,
                organization_id=payload.organization_id,
            )

    raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")


def require_role(minimum_role: UserRole):
    """Dependency that gates access based on user role.

    Usage:
        @router.get("/admin/users")
        async def list_users(user: CurrentUser = Depends(require_role(UserRole.MAIN_ADMIN))):
            ...

        @router.get("/org/settings")
        async def org_settings(user: CurrentUser = Depends(require_role(UserRole.ORG_ADMIN))):
            ...
    """

    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_role(minimum_role):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": f"This action requires {minimum_role.value} role or higher.",
                    "required_role": minimum_role.value,
                    "current_role": user.role.value,
                },
            )
        return user

    return dependency


def require_plan(minimum_plan: str):
    """Dependency that gates access based on the user's access tier.

    Access tier hierarchy: free < pro < business

    Usage:
        @router.get("/reports")
        async def get_reports(user: CurrentUser = Depends(require_plan("pro"))):
            ...
    """
    plan_hierarchy = {"free": 0, "pro": 1, "business": 2}

    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        # Main admins bypass plan checks
        if user.is_admin:
            return user

        user_level = plan_hierarchy.get(user.plan, 0)
        required_level = plan_hierarchy.get(minimum_plan, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "plan_required",
                    "message": f"This feature requires the {minimum_plan.title()} plan or higher.",
                    "required_plan": minimum_plan,
                    "current_plan": user.plan,
                    "upgrade_url": "/pricing",
                },
            )
        return user

    return dependency


def require_main_admin():
    """Dependency that gates routes to the platform main admin only.

    Usage:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(user: CurrentUser = Depends(require_main_admin())):
            ...
    """
    return require_role(UserRole.MAIN_ADMIN)


def require_org_admin():
    """Dependency that gates routes to organization admins.

    Ensures the user is at least an org_admin and belongs to an organization.

    Usage:
        @router.get("/org/members")
        async def list_members(user: CurrentUser = Depends(require_org_admin())):
            ...
    """

    async def dependency(user: CurrentUser = Depends(require_role(UserRole.ORG_ADMIN))) -> CurrentUser:
        if not user.organization_id and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="You are not associated with any organization.",
            )
        return user

    return dependency

"""
Auth interfaces — abstract base class for pluggable auth providers.
"""

from abc import ABC, abstractmethod

from .models import CurrentUser


class AuthProvider(ABC):
    """Abstract interface for authentication providers.

    Implement this interface to integrate your preferred auth service
    (e.g., Auth0, Firebase Auth, Clerk, custom JWT, etc.).

    The boilerplate ships with a MockAuthProvider for development
    and testing. For production, create your own implementation.

    Example:
        class MyAuthProvider(AuthProvider):
            async def verify_token(self, token: str) -> CurrentUser | None:
                # Verify token with your auth service
                payload = decode_jwt(token)
                return CurrentUser(id=payload["sub"], email=payload["email"])

            async def get_user_by_id(self, user_id: str) -> CurrentUser | None:
                # Fetch user from your database
                row = await db.fetch_user(user_id)
                return CurrentUser(**row) if row else None
    """

    @abstractmethod
    async def verify_token(self, token: str) -> CurrentUser | None:
        """Verify an authentication token and return the user context.

        Args:
            token: The bearer token from the Authorization header.

        Returns:
            CurrentUser if valid, None if the token is invalid.

        Raises:
            Exception: If the auth service is unavailable.
        """
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> CurrentUser | None:
        """Fetch a user by their unique identifier.

        Args:
            user_id: The user's unique ID.

        Returns:
            CurrentUser if found, None otherwise.
        """
        ...

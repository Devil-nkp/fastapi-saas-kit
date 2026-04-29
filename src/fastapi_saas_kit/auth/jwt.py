"""
JWT utilities — token creation and verification.
"""

import time

import jwt

from ..config import get_settings
from .models import TokenPayload


def create_access_token(
    user_id: str,
    email: str,
    role: str = "user",
    plan: str = "free",
    organization_id: str | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        user_id: Unique user identifier (becomes the 'sub' claim).
        email: User's email address.
        role: User role (user, org_admin, main_admin).
        plan: User's current plan.
        organization_id: Optional organization the user belongs to.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "plan": plan,
        "iat": now,
        "exp": now + (settings.AUTH_JWT_EXPIRY_MINUTES * 60),
    }
    if organization_id:
        payload["organization_id"] = organization_id

    return jwt.encode(payload, settings.AUTH_JWT_SECRET, algorithm=settings.AUTH_JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode and verify a JWT access token.

    Args:
        token: The JWT string to decode.

    Returns:
        TokenPayload if valid, None if the token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET,
            algorithms=[settings.AUTH_JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

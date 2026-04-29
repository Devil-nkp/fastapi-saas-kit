# Authentication

## Overview

fastapi-saas-kit uses a pluggable `AuthProvider` interface for authentication. This allows you to use any auth service (Auth0, Firebase, Clerk, custom JWT, etc.) without changing your application code.

## AuthProvider Interface

```python
from fastapi_saas_kit.auth.interfaces import AuthProvider
from fastapi_saas_kit.auth.models import CurrentUser

class AuthProvider(ABC):
    async def verify_token(self, token: str) -> CurrentUser | None: ...
    async def get_user_by_id(self, user_id: str) -> CurrentUser | None: ...
```

## MockAuthProvider (Development)

For local development and testing, use the included `MockAuthProvider`:

```python
from fastapi_saas_kit.auth.mock import MockAuthProvider
from fastapi_saas_kit.auth.dependencies import configure_auth

configure_auth(MockAuthProvider())
```

Mock tokens use the format `mock-{user_id}`:

| Token | User | Role | Access Tier |
|-------|------|------|------|
| `mock-user-001` | user@example.com | user | free |
| `mock-user-002` | pro@example.com | user | pro |
| `mock-org-admin-001` | orgadmin@example.com | org_admin | advanced |
| `mock-main-admin-001` | admin@example.com | main_admin | advanced |

## JWT Authentication

For production, use the built-in JWT utilities:

```python
from fastapi_saas_kit.auth.jwt import create_access_token, decode_access_token

# Create a token
token = create_access_token(
    user_id="user-123",
    email="user@example.com",
    role="user",
    plan="pro",  # access tier stored in the existing user model
)

# Decode a token
payload = decode_access_token(token)
```

## Adding Your Own Auth Provider

1. Create a class that implements `AuthProvider`:

```python
from fastapi_saas_kit.auth.interfaces import AuthProvider
from fastapi_saas_kit.auth.models import CurrentUser

class MyAuthProvider(AuthProvider):
    async def verify_token(self, token: str) -> CurrentUser | None:
        # Call your auth service to verify the token
        user_data = await my_auth_service.verify(token)
        if not user_data:
            return None
        return CurrentUser(
            id=user_data["id"],
            email=user_data["email"],
            role=user_data.get("role", "user"),
            plan=user_data.get("plan", "free"),
        )

    async def get_user_by_id(self, user_id: str) -> CurrentUser | None:
        user_data = await my_auth_service.get_user(user_id)
        return CurrentUser(**user_data) if user_data else None
```

2. Configure it during application initialization:

```python
from fastapi_saas_kit.auth.dependencies import configure_auth
configure_auth(MyAuthProvider())
```

## Using Auth in Routes

```python
from fastapi import Depends
from fastapi_saas_kit.auth.dependencies import get_current_user, require_plan, require_role
from fastapi_saas_kit.auth.models import CurrentUser, UserRole

# Any authenticated user
@app.get("/profile")
async def profile(user: CurrentUser = Depends(get_current_user)):
    return {"email": user.email}

# Requires a specific access tier
@app.get("/advanced")
async def advanced(user: CurrentUser = Depends(require_plan("pro"))):
    return {"message": "Advanced workspace access"}

# Requires specific role
@app.get("/admin")
async def admin(user: CurrentUser = Depends(require_role(UserRole.MAIN_ADMIN))):
    return {"message": "Admin panel"}
```

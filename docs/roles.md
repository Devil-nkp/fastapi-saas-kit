# Roles and Permissions

## Role Hierarchy

fastapi-saas-kit supports three roles with hierarchical access:

```
main_admin (level 2) -> Full platform access
    ^
org_admin  (level 1) -> Organization management
    ^
user       (level 0) -> Basic authenticated access
```

## Role Details

### `user` (Default)
- Access their own profile and data
- View their organization's shared data
- Use features allowed by their access tier

### `org_admin`
- Everything a user can do, plus:
- View and manage organization settings
- Add/remove organization members
- View organization analytics

### `main_admin`
- Everything an org_admin can do, plus:
- Access all organizations
- Create and manage organizations
- Bypass access tier and quota limits
- Access admin-only endpoints

## Using Role Gates

```python
from fastapi import Depends
from fastapi_saas_kit.auth.dependencies import (
    get_current_user,      # Any authenticated user
    require_role,          # Specific role minimum
    require_org_admin,     # org_admin + must have organization
    require_main_admin,    # main_admin only
)
from fastapi_saas_kit.auth.models import UserRole

# Any authenticated user
@router.get("/profile")
async def profile(user = Depends(get_current_user)): ...

# Org admin or higher
@router.get("/org/settings")
async def settings(user = Depends(require_org_admin())): ...

# Main admin only
@router.delete("/admin/users/{id}")
async def delete_user(user = Depends(require_main_admin())): ...

# Custom role check
@router.get("/reports")
async def reports(user = Depends(require_role(UserRole.ORG_ADMIN))): ...
```

## Checking Roles in Code

```python
user = await get_current_user(request)

if user.is_admin:          # main_admin only
    ...
if user.is_org_admin:      # org_admin or main_admin
    ...
if user.has_role(UserRole.ORG_ADMIN):  # org_admin or higher
    ...
```

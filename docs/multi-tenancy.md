# Multi-Tenancy

## Overview

fastapi-saas-kit provides a multi-tenant architecture where each **organization** is a tenant with isolated data, members, and configuration.

## Tenant Isolation

The core principle: **users can only access data belonging to their organization**.

```
Main Admin → Can access ALL organizations
Org Admin  → Can manage ONLY their organization
User       → Can access ONLY their organization's data
```

## Organization Model

Each organization has:

| Field | Description |
|-------|-------------|
| `id` | Unique UUID |
| `name` | Display name |
| `slug` | URL-safe unique identifier |
| `plan` | Subscription plan (free, pro, business) |
| `seat_limit` | Maximum number of members |
| `seats_used` | Current member count |
| `status` | active, suspended, expired, pending |

## Tenant-Scoped Queries

Always scope database queries by `organization_id`:

```python
# ✅ Correct — scoped to user's organization
async def get_projects(user: CurrentUser):
    return await db.fetch(
        "SELECT * FROM projects WHERE organization_id = $1",
        user.organization_id,
    )

# ❌ Wrong — leaks data across tenants
async def get_projects():
    return await db.fetch("SELECT * FROM projects")
```

## Organization Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/orgs/` | main_admin | List all organizations |
| POST | `/orgs/` | main_admin | Create organization |
| GET | `/orgs/my` | org_admin | View own organization |
| GET | `/orgs/{id}` | main_admin | View specific org |
| GET | `/orgs/{id}/members` | org_admin / main_admin | List members |
| POST | `/orgs/{id}/members` | org_admin / main_admin | Add member |
| DELETE | `/orgs/{id}/members/{uid}` | org_admin / main_admin | Remove member |

## Seat Management

Organizations have seat limits based on their plan. The system automatically:
- Tracks `seats_used` when members are added/removed
- Rejects new members when at capacity
- Links users to their organization via `organization_id`

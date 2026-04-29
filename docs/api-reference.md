# API Reference

## Health Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/HEAD | `/` | None | Root health probe |
| GET | `/health` | None | Basic health check |
| GET | `/health/ready` | None | Readiness check with database status |

## Organization Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/orgs/` | main_admin | List all organizations |
| POST | `/orgs/` | main_admin | Create organization |
| GET | `/orgs/my` | org_admin | View own organization |
| GET | `/orgs/{org_id}` | main_admin | View specific organization |
| GET | `/orgs/{org_id}/members` | org_admin / main_admin | List organization members |
| POST | `/orgs/{org_id}/members` | org_admin / main_admin | Add member |
| DELETE | `/orgs/{org_id}/members/{user_id}` | org_admin / main_admin | Remove member |

## Access Gate Endpoints

The route paths use the existing `/billing` prefix for compatibility with the current code. Public-facing applications can expose these as access, entitlement, or provider-adapter routes.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/billing/create-order` | user | Create an access request |
| POST | `/billing/verify-payment` | user | Verify provider callback data |
| POST | `/billing/webhook` | none | Handle provider webhook |
| GET | `/billing/status` | user | Get access status |

## Authentication

All authenticated endpoints require a `Bearer` token in the `Authorization` header:

```text
Authorization: Bearer <token>
```

### Mock Tokens

```text
Bearer mock-user-001          -> Free-tier user
Bearer mock-user-002          -> Pro-tier user
Bearer mock-org-admin-001     -> Org admin with advanced tier
Bearer mock-main-admin-001    -> Platform admin with advanced tier
```

## Error Responses

All errors return a consistent JSON structure:

```json
{
  "error": true,
  "status_code": 403,
  "detail": {
    "error": "plan_required",
    "message": "This feature requires the Pro access tier or higher.",
    "required_plan": "pro",
    "current_plan": "free",
    "upgrade_url": "/access"
  }
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Not authenticated |
| 402 | Usage limit exceeded |
| 403 | Insufficient permissions or access tier |
| 404 | Not found |
| 409 | Conflict |
| 429 | Rate limited |
| 500 | Server error |
| 503 | Service unavailable |

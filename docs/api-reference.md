# API Reference

## Health Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/HEAD | `/` | None | Root health probe |
| GET | `/health` | None | Basic health check |
| GET | `/health/ready` | None | Readiness check (includes DB) |

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

## Billing Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/billing/create-order` | user | Create billing order |
| POST | `/billing/verify-payment` | user | Verify payment |
| POST | `/billing/webhook` | none | Handle webhook |
| GET | `/billing/status` | user | Get billing status |

## Authentication

All authenticated endpoints require a `Bearer` token in the `Authorization` header:

```
Authorization: Bearer <token>
```

### Mock Tokens (Development)

```
Bearer mock-user-001          → Free user
Bearer mock-user-002          → Pro user
Bearer mock-org-admin-001     → Org admin (business)
Bearer mock-main-admin-001    → Platform admin (business)
```

## Error Responses

All errors return a consistent JSON structure:

```json
{
  "error": true,
  "status_code": 403,
  "detail": {
    "error": "plan_required",
    "message": "This feature requires the Pro plan or higher.",
    "required_plan": "pro",
    "current_plan": "free",
    "upgrade_url": "/pricing"
  }
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Not authenticated |
| 402 | Quota exceeded |
| 403 | Insufficient permissions or plan |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 429 | Rate limited |
| 500 | Server error |
| 503 | Service unavailable (DB not ready) |

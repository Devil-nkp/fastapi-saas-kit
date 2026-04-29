"""
Multi-Tenant App Example - organization-scoped application.

Demonstrates:
- Organization-scoped endpoints
- Role-based access control
- Tenant data isolation
- Provider adapter and quota integration

Run:
    python main.py
    # Visit http://localhost:8001/docs
"""

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from fastapi_saas_kit.auth.dependencies import (
    configure_auth,
    get_current_user,
    require_main_admin,
    require_org_admin,
)
from fastapi_saas_kit.auth.mock import MockAuthProvider
from fastapi_saas_kit.auth.models import CurrentUser
from fastapi_saas_kit.billing.adapters.mock import MockBillingProvider
from fastapi_saas_kit.billing.router import configure_billing
from fastapi_saas_kit.plans.config import has_feature
from fastapi_saas_kit.plans.quota import check_quota, get_usage_stats

app = FastAPI(title="Multi-Tenant Backend Example", version="1.0.0")

# Configure providers
configure_auth(MockAuthProvider())
configure_billing(MockBillingProvider())

# Simulated per-user usage tracking
_user_usage: dict[str, dict[str, int]] = {}


def _get_user_usage(user_id: str) -> dict[str, int]:
    if user_id not in _user_usage:
        _user_usage[user_id] = {"monthly_requests": 0, "projects": 0}
    return _user_usage[user_id]


@app.get("/")
async def root():
    return {
        "message": "Multi-Tenant Backend Example",
        "docs": "/docs",
        "endpoints": [
            "GET /my-org - View your organization",
            "GET /projects - List projects with usage tracking",
            "POST /projects - Create project with quota enforcement",
            "GET /admin/orgs - List all orgs (admin only)",
            "GET /usage - View your usage stats",
        ],
    }


@app.get("/my-org")
async def get_my_org(user: CurrentUser = Depends(require_org_admin())):
    """View your organization. Requires org_admin role."""
    return {
        "message": f"Organization details for {user.email}",
        "organization_id": user.organization_id,
        "role": user.role.value,
        "access_tier": user.plan,
    }


@app.get("/projects")
async def list_projects(user: CurrentUser = Depends(get_current_user)):
    """List projects for the current user's organization."""
    if not user.organization_id and not user.is_admin:
        return {"projects": [], "message": "Join an organization to see projects."}

    usage = _get_user_usage(user.id)
    usage["monthly_requests"] += 1

    return {
        "organization_id": user.organization_id,
        "projects": [
            {"id": "proj-001", "name": "Website Redesign"},
            {"id": "proj-002", "name": "Mobile App"},
        ],
        "total_requests_used": usage["monthly_requests"],
    }


@app.post("/projects")
async def create_project(
    name: str = "New Project",
    user: CurrentUser = Depends(get_current_user),
):
    """Create a project. Enforces quota limits."""
    usage = _get_user_usage(user.id)
    await check_quota(user, "projects", usage.get("projects", 0))
    usage["projects"] = usage.get("projects", 0) + 1

    return {
        "message": f"Project '{name}' created!",
        "projects_used": usage["projects"],
    }


@app.get("/analytics")
async def get_analytics(user: CurrentUser = Depends(get_current_user)):
    """View analytics. Requires advanced_analytics feature."""
    if not user.is_admin and not has_feature(user.plan, "advanced_analytics"):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Advanced analytics requires Pro access tier or higher.",
                "access_url": "/access",
            },
        )

    return {
        "views": 5678,
        "unique_visitors": 1234,
        "event_rate": "4.2%",
    }


@app.get("/usage")
async def get_usage(user: CurrentUser = Depends(get_current_user)):
    """View your current usage statistics."""
    usage = _get_user_usage(user.id)
    stats = get_usage_stats(user.plan, usage)
    return {"access_tier": user.plan, "usage": stats}


@app.get("/admin/orgs")
async def admin_list_orgs(user: CurrentUser = Depends(require_main_admin())):
    """List all organizations. Main admin only."""
    return {
        "organizations": [
            {"id": "org-001", "name": "Platform Team", "plan": "advanced", "members": 45},
            {"id": "org-002", "name": "Project Team", "plan": "pro", "members": 8},
            {"id": "org-003", "name": "Solo Dev", "plan": "free", "members": 1},
        ],
        "total": 3,
    }


if __name__ == "__main__":
    print("\nMulti-Tenant Backend Example")
    print("   Docs: http://localhost:8001/docs")
    print("   Use 'Authorization: Bearer mock-user-001' for regular user")
    print("   Use 'Authorization: Bearer mock-org-admin-001' for org admin")
    print("   Use 'Authorization: Bearer mock-main-admin-001' for platform admin\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)

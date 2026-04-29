"""
Basic Backend Example - minimal single-tenant application.

Demonstrates:
- FastAPI app with authentication
- Access-tier gated endpoints
- Quota checking
- Health checks

Run:
    python main.py
    # Visit http://localhost:8000/docs
"""

import uvicorn
from fastapi import Depends, FastAPI

from fastapi_saas_kit.auth.dependencies import (
    configure_auth,
    get_current_user,
    require_plan,
)
from fastapi_saas_kit.auth.mock import MockAuthProvider
from fastapi_saas_kit.auth.models import CurrentUser
from fastapi_saas_kit.plans.config import get_plan_config

app = FastAPI(title="Basic Backend Example", version="1.0.0")

# Configure mock auth for development
configure_auth(MockAuthProvider())


@app.get("/")
async def root():
    return {"message": "Welcome to the Basic Backend Example!", "docs": "/docs"}


@app.get("/profile")
async def get_profile(user: CurrentUser = Depends(get_current_user)):
    """Get the current user's profile. Requires authentication."""
    plan_config = get_plan_config(user.plan)
    return {
        "id": user.id,
        "email": user.email,
        "access_tier": user.plan,
        "role": user.role.value,
        "access_tier_details": {
            "name": plan_config["display_name"],
        },
    }


@app.get("/dashboard")
async def get_dashboard(user: CurrentUser = Depends(get_current_user)):
    """Basic dashboard available to all authenticated users."""
    return {
        "message": f"Welcome back, {user.email}!",
        "access_tier": user.plan,
        "features_available": list(k for k, v in get_plan_config(user.plan).get("features", {}).items() if v),
    }


@app.get("/analytics")
async def get_analytics(user: CurrentUser = Depends(require_plan("pro"))):
    """Advanced analytics requires Pro access tier or higher."""
    return {
        "message": "Here are your advanced analytics.",
        "access_tier": user.plan,
        "data": {"views": 1234, "events": 56, "quota_units_used": 789},
    }


@app.get("/workspace")
async def get_workspace(user: CurrentUser = Depends(require_plan("pro"))):
    """Advanced workspace features require Pro access tier or higher."""
    return {
        "message": "Welcome to advanced workspace features.",
        "sso_enabled": True,
        "custom_branding": True,
    }


if __name__ == "__main__":
    print("\nBasic Backend Example")
    print("   Docs: http://localhost:8000/docs")
    print("   Use 'Authorization: Bearer mock-user-001' for free user")
    print("   Use 'Authorization: Bearer mock-user-002' for pro user")
    print("   Use 'Authorization: Bearer mock-main-admin-001' for admin\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

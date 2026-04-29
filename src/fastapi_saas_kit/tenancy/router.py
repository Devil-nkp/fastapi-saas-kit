"""
Tenancy router — CRUD endpoints for organizations and members.
"""

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import get_current_user, require_main_admin, require_org_admin
from ..auth.models import CurrentUser
from . import service
from .models import OrganizationCreate, OrgMemberAdd

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.get("/")
async def list_organizations(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    user: CurrentUser = Depends(require_main_admin()),
):
    """List all organizations. Main admin only."""
    orgs = await service.list_organizations(status=status, limit=limit, offset=offset)
    return {"organizations": orgs, "count": len(orgs)}


@router.post("/", status_code=201)
async def create_organization(
    body: OrganizationCreate,
    user: CurrentUser = Depends(require_main_admin()),
):
    """Create a new organization. Main admin only."""
    existing = await service.get_organization_by_slug(body.slug)
    if existing:
        raise HTTPException(status_code=409, detail="Organization slug already exists.")

    org = await service.create_organization(
        name=body.name,
        slug=body.slug,
        plan=body.plan,
        seat_limit=body.seat_limit,
        created_by=user.id,
    )
    return {"organization": org, "message": "Organization created successfully."}


@router.get("/my")
async def get_my_organization(
    user: CurrentUser = Depends(require_org_admin()),
):
    """Get the current user's organization details."""
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="You are not associated with any organization.")

    org = await service.get_organization(user.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return {"organization": org}


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    user: CurrentUser = Depends(require_main_admin()),
):
    """Get organization details by ID. Main admin only."""
    org = await service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return {"organization": org}


@router.get("/{org_id}/members")
async def list_members(
    org_id: str,
    limit: int = 50,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user),
):
    """List organization members.

    Org admins can only list members of their own organization.
    Main admins can list members of any organization.
    """
    if not user.is_admin and user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="You can only view members of your own organization.")

    members = await service.get_org_members(org_id, limit=limit, offset=offset)
    return {"members": members, "count": len(members)}


@router.post("/{org_id}/members", status_code=201)
async def add_member(
    org_id: str,
    body: OrgMemberAdd,
    user: CurrentUser = Depends(get_current_user),
):
    """Add a member to an organization.

    Org admins can only add to their own organization.
    Main admins can add to any organization.
    """
    if not user.is_admin and user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="You can only manage your own organization.")

    if not user.is_org_admin:
        raise HTTPException(status_code=403, detail="Only organization admins can add members.")

    member = await service.add_org_member(org_id, body.user_id, body.role)
    if not member:
        raise HTTPException(status_code=400, detail="Could not add member. Seat limit may have been reached.")

    return {"member": member, "message": "Member added successfully."}


@router.delete("/{org_id}/members/{user_id}")
async def remove_member(
    org_id: str,
    user_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Remove a member from an organization."""
    if not user.is_admin and user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="You can only manage your own organization.")

    if not user.is_org_admin:
        raise HTTPException(status_code=403, detail="Only organization admins can remove members.")

    removed = await service.remove_org_member(org_id, user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Member not found in this organization.")

    return {"message": "Member removed successfully."}

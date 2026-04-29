"""
Tenancy models — organization and member data structures.
"""

from pydantic import BaseModel


class Organization(BaseModel):
    """Represents a tenant organization in the platform."""

    id: str
    name: str
    slug: str
    plan: str = "free"
    seat_limit: int = 5
    seats_used: int = 0
    status: str = "active"


class OrganizationCreate(BaseModel):
    """Request model for creating an organization."""

    name: str
    slug: str
    plan: str = "free"
    seat_limit: int = 5


class OrganizationUpdate(BaseModel):
    """Request model for updating an organization."""

    name: str | None = None
    plan: str | None = None
    seat_limit: int | None = None
    status: str | None = None


class OrgMember(BaseModel):
    """Represents a member within an organization."""

    id: str
    organization_id: str
    user_id: str
    role: str = "member"
    status: str = "active"


class OrgMemberAdd(BaseModel):
    """Request model for adding a member to an organization."""

    user_id: str
    role: str = "member"


class OrgAdminContext(BaseModel):
    """Context object for organization admin requests.

    Provides the admin's user context along with their
    organization details for tenant-scoped operations.
    """

    user_id: str
    email: str
    organization_id: str
    organization_name: str
    org_slug: str
    org_status: str
    admin_role: str = "admin"

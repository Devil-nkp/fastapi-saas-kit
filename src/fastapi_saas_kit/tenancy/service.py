"""
Tenancy service - tenant-scoped data access patterns.
"""

import structlog

from ..database.connection import DatabaseConnection

logger = structlog.get_logger("saas_kit.tenancy")


async def get_organization(org_id: str) -> dict | None:
    """Fetch an organization by ID.

    Args:
        org_id: The organization's UUID.

    Returns:
        Organization dict or None if not found.
    """
    async with DatabaseConnection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM organizations WHERE id = $1",
            org_id,
        )
        return dict(row) if row else None


async def get_organization_by_slug(slug: str) -> dict | None:
    """Fetch an organization by its unique slug.

    Args:
        slug: The organization's URL-safe slug.

    Returns:
        Organization dict or None if not found.
    """
    async with DatabaseConnection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM organizations WHERE slug = $1",
            slug,
        )
        return dict(row) if row else None


async def create_organization(name: str, slug: str, plan: str = "free", seat_limit: int = 5, created_by: str | None = None) -> dict:
    """Create a new organization (tenant).

    Args:
        name: Display name for the organization.
        slug: URL-safe unique identifier.
        plan: Internal access tier key.
        seat_limit: Maximum number of members.
        created_by: User ID of the creator.

    Returns:
        The newly created organization dict.
    """
    async with DatabaseConnection() as conn:
        row = await conn.fetchrow(
            """INSERT INTO organizations (name, slug, plan, seat_limit, created_by)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING *""",
            name, slug, plan, seat_limit, created_by,
        )
        logger.info("organization_created", org_id=str(row["id"]), slug=slug)
        return dict(row)


async def list_organizations(status: str | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
    """List organizations with optional status filter.

    Args:
        status: Filter by status (active, suspended, etc.).
        limit: Maximum results to return.
        offset: Pagination offset.

    Returns:
        List of organization dicts.
    """
    async with DatabaseConnection() as conn:
        if status:
            rows = await conn.fetch(
                "SELECT * FROM organizations WHERE status = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                status, limit, offset,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM organizations ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit, offset,
            )
        return [dict(row) for row in rows]


async def get_org_members(org_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """List members of an organization.

    This is a tenant-scoped query - only returns members
    belonging to the specified organization.

    Args:
        org_id: Organization UUID.
        limit: Maximum results.
        offset: Pagination offset.

    Returns:
        List of member dicts.
    """
    async with DatabaseConnection() as conn:
        rows = await conn.fetch(
            """SELECT om.*, u.email, u.full_name
               FROM organization_members om
               JOIN users u ON u.id = om.user_id
               WHERE om.organization_id = $1
               ORDER BY om.joined_at DESC
               LIMIT $2 OFFSET $3""",
            org_id, limit, offset,
        )
        return [dict(row) for row in rows]


async def add_org_member(org_id: str, user_id: str, role: str = "member") -> dict | None:
    """Add a member to an organization.

    Checks seat limits before adding. Returns None if at capacity.

    Args:
        org_id: Organization UUID.
        user_id: User UUID to add.
        role: Member role (member, admin, owner).

    Returns:
        The new membership dict, or None if seat limit reached.
    """
    async with DatabaseConnection() as conn:
        # Check seat limit
        org = await conn.fetchrow(
            "SELECT seat_limit, seats_used FROM organizations WHERE id = $1",
            org_id,
        )
        if not org:
            return None

        if org["seats_used"] >= org["seat_limit"]:
            logger.warning("seat_limit_reached", org_id=org_id)
            return None

        row = await conn.fetchrow(
            """INSERT INTO organization_members (organization_id, user_id, role)
               VALUES ($1, $2, $3)
               ON CONFLICT (organization_id, user_id) DO NOTHING
               RETURNING *""",
            org_id, user_id, role,
        )

        if row:
            await conn.execute(
                "UPDATE organizations SET seats_used = seats_used + 1 WHERE id = $1",
                org_id,
            )
            # Link user to organization
            await conn.execute(
                "UPDATE users SET organization_id = $1 WHERE id = $2",
                org_id, user_id,
            )
            logger.info("member_added", org_id=org_id, user_id=user_id)

        return dict(row) if row else None


async def remove_org_member(org_id: str, user_id: str) -> bool:
    """Remove a member from an organization.

    Args:
        org_id: Organization UUID.
        user_id: User UUID to remove.

    Returns:
        True if removed, False if member not found.
    """
    async with DatabaseConnection() as conn:
        result = await conn.execute(
            "DELETE FROM organization_members WHERE organization_id = $1 AND user_id = $2",
            org_id, user_id,
        )

        if "DELETE 1" in result:
            await conn.execute(
                "UPDATE organizations SET seats_used = GREATEST(0, seats_used - 1) WHERE id = $1",
                org_id,
            )
            await conn.execute(
                "UPDATE users SET organization_id = NULL WHERE id = $1 AND organization_id = $2",
                user_id, org_id,
            )
            logger.info("member_removed", org_id=org_id, user_id=user_id)
            return True

        return False

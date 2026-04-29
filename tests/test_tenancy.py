"""
Tests for multi-tenancy and organization isolation.
"""


def test_org_admin_can_view_own_org(client, org_admin_headers, monkeypatch):
    """Org admins should be able to view their own organization."""
    from fastapi_saas_kit.tenancy import service

    async def get_organization(org_id: str):
        return {"id": org_id, "name": "Test Org", "slug": "test-org", "plan": "pro"}

    monkeypatch.setattr(service, "get_organization", get_organization)

    response = client.get("/orgs/my", headers=org_admin_headers)
    assert response.status_code == 200


def test_regular_user_cannot_list_all_orgs(client, auth_headers):
    """Regular users should not be able to list all organizations."""
    response = client.get("/orgs/", headers=auth_headers("user-001"))
    assert response.status_code == 403
    data = response.json()
    assert "insufficient_permissions" in str(data.get("detail", ""))


def test_admin_can_list_all_orgs(client, admin_headers, monkeypatch):
    """Main admins should be able to list all organizations."""
    from fastapi_saas_kit.tenancy import service

    async def list_organizations(status=None, limit=50, offset=0):
        return []

    monkeypatch.setattr(service, "list_organizations", list_organizations)

    response = client.get("/orgs/", headers=admin_headers)
    assert response.status_code == 200


class TestTenancyModels:
    """Test tenancy data models."""

    def test_organization_model(self):
        from fastapi_saas_kit.tenancy.models import Organization

        org = Organization(
            id="org-001",
            name="Test Corp",
            slug="test-corp",
            plan="pro",
            seat_limit=10,
        )
        assert org.name == "Test Corp"
        assert org.slug == "test-corp"
        assert org.plan == "pro"
        assert org.status == "active"

    def test_org_member_model(self):
        from fastapi_saas_kit.tenancy.models import OrgMember

        member = OrgMember(
            id="mem-001",
            organization_id="org-001",
            user_id="user-001",
            role="admin",
        )
        assert member.organization_id == "org-001"
        assert member.role == "admin"
        assert member.status == "active"

    def test_org_admin_context(self):
        from fastapi_saas_kit.tenancy.models import OrgAdminContext

        ctx = OrgAdminContext(
            user_id="user-001",
            email="admin@test.com",
            organization_id="org-001",
            organization_name="Test Corp",
            org_slug="test-corp",
            org_status="active",
        )
        assert ctx.organization_id == "org-001"
        assert ctx.admin_role == "admin"

"""
Tests for authentication and RBAC.
"""

import pytest


def test_unauthenticated_request_returns_401(client):
    """Requests without auth token should be rejected."""
    response = client.get("/orgs/")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated. Please provide a valid token."


def test_mock_auth_returns_user(client, auth_headers):
    """Mock auth should resolve a valid user from token."""
    # The billing status endpoint requires auth
    response = client.get("/billing/status", headers=auth_headers("user-001"))
    assert response.status_code == 200


def test_admin_token_resolves_admin(client, admin_headers, monkeypatch):
    """Admin mock token should resolve to admin user."""
    from fastapi_saas_kit.tenancy import service

    async def list_organizations(status=None, limit=50, offset=0):
        return []

    monkeypatch.setattr(service, "list_organizations", list_organizations)

    response = client.get("/orgs/", headers=admin_headers)
    # Should succeed because main admin has access
    assert response.status_code == 200


def test_non_admin_cannot_list_orgs(client, auth_headers):
    """Regular users should not be able to list all organizations."""
    response = client.get("/orgs/", headers=auth_headers("user-001"))
    assert response.status_code == 403


def test_invalid_token_returns_401(client):
    """Invalid token should return 401."""
    response = client.get("/billing/status", headers={"Authorization": "Bearer "})
    assert response.status_code == 401


def test_empty_bearer_returns_401(client):
    """Empty bearer token should return 401."""
    response = client.get("/billing/status", headers={"Authorization": "Bearer"})
    assert response.status_code == 401


class TestRoleHierarchy:
    """Test role hierarchy checks."""

    def test_user_role_model(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.USER)
        assert not user.is_admin
        assert not user.is_org_admin
        assert user.has_role(UserRole.USER)
        assert not user.has_role(UserRole.ORG_ADMIN)
        assert not user.has_role(UserRole.MAIN_ADMIN)

    def test_org_admin_role_model(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.ORG_ADMIN)
        assert not user.is_admin
        assert user.is_org_admin
        assert user.has_role(UserRole.USER)
        assert user.has_role(UserRole.ORG_ADMIN)
        assert not user.has_role(UserRole.MAIN_ADMIN)

    def test_main_admin_role_model(self):
        from fastapi_saas_kit.auth.models import CurrentUser, UserRole

        user = CurrentUser(id="1", email="test@test.com", role=UserRole.MAIN_ADMIN)
        assert user.is_admin
        assert user.is_org_admin
        assert user.has_role(UserRole.USER)
        assert user.has_role(UserRole.ORG_ADMIN)
        assert user.has_role(UserRole.MAIN_ADMIN)


class TestMockAuthProvider:
    """Test MockAuthProvider behavior."""

    @pytest.mark.asyncio
    async def test_mock_token_resolves_user(self):
        from fastapi_saas_kit.auth.mock import MockAuthProvider

        provider = MockAuthProvider()
        user = await provider.verify_token("mock-user-001")
        assert user is not None
        assert user.id == "user-001"
        assert user.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_mock_admin_token(self):
        from fastapi_saas_kit.auth.mock import MockAuthProvider

        provider = MockAuthProvider()
        user = await provider.verify_token("mock-main-admin-001")
        assert user is not None
        assert user.is_admin

    @pytest.mark.asyncio
    async def test_empty_token_returns_none(self):
        from fastapi_saas_kit.auth.mock import MockAuthProvider

        provider = MockAuthProvider()
        user = await provider.verify_token("")
        assert user is None

    @pytest.mark.asyncio
    async def test_unknown_mock_id_returns_none(self):
        from fastapi_saas_kit.auth.mock import MockAuthProvider

        provider = MockAuthProvider()
        user = await provider.verify_token("mock-nonexistent-999")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self):
        from fastapi_saas_kit.auth.mock import MockAuthProvider

        provider = MockAuthProvider()
        user = await provider.get_user_by_id("user-001")
        assert user is not None
        assert user.email == "user@example.com"

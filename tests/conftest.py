"""
Shared test fixtures and configuration.
"""

import os

import pytest
from fastapi.testclient import TestClient

from fastapi_saas_kit.app import create_app
from fastapi_saas_kit.auth.dependencies import configure_auth
from fastapi_saas_kit.auth.mock import MockAuthProvider
from fastapi_saas_kit.billing.adapters.mock import MockBillingProvider
from fastapi_saas_kit.billing.router import configure_billing
from fastapi_saas_kit.config import get_settings


@pytest.fixture(scope="session")
def app():
    """Create a test application instance."""
    os.environ["AUTH_PROVIDER"] = "mock"
    os.environ["BILLING_PROVIDER"] = "mock"
    os.environ["CACHE_PROVIDER"] = "memory"
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/saas_kit_test"
    get_settings.cache_clear()

    application = create_app()
    configure_auth(MockAuthProvider())
    configure_billing(MockBillingProvider())
    return application


@pytest.fixture(scope="session")
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return a helper function to generate auth headers for mock users."""

    def _headers(user_id: str = "user-001"):
        return {"Authorization": f"Bearer mock-{user_id}"}

    return _headers


@pytest.fixture
def admin_headers():
    """Auth headers for the main admin user."""
    return {"Authorization": "Bearer mock-main-admin-001"}


@pytest.fixture
def org_admin_headers():
    """Auth headers for an organization admin."""
    return {"Authorization": "Bearer mock-org-admin-001"}

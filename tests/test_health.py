"""
Tests for health check endpoints.
"""


def test_root_endpoint(client):
    """Root endpoint should return 200 with service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_health_endpoint(client):
    """Health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "starting")
    assert "database" in data
    assert "uptime_seconds" in data
    assert "environment" in data


def test_health_ready_returns_status(client):
    """Health ready endpoint should return a status code."""
    response = client.get("/health/ready")
    # May be 200 (ready) or 503 (starting) depending on DB state
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_root_head_method(client):
    """Root endpoint should support HEAD method for probes."""
    response = client.head("/")
    assert response.status_code == 200


def test_health_cache_headers(client):
    """Health endpoints should include no-cache headers."""
    response = client.get("/health")
    assert response.headers.get("Cache-Control") is not None
    assert "no-store" in response.headers["Cache-Control"]

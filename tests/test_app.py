"""Tests for general app endpoints"""
import pytest


def test_root_endpoint_returns_redirect(client):
    """Test that root endpoint returns a redirect"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "static/index.html" in response.headers["location"]


def test_root_endpoint_redirects_to_index(client):
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=True)
    # The static file will return 200 with HTML content
    assert response.status_code == 200


def test_static_files_accessible(client):
    """Test that static files are accessible"""
    # Test that we can access the static directory
    response = client.get("/static/index.html")
    assert response.status_code == 200


def test_activities_endpoint_exists(client):
    """Test that the /activities endpoint is accessible"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_signup_endpoint_exists(client):
    """Test that the signup endpoint is accessible"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    # 200 for success or 400 for duplicate - both mean endpoint exists
    assert response.status_code in [200, 400]


def test_unregister_endpoint_exists(client):
    """Test that the unregister endpoint is accessible"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    # 200 for success or 400 for error - both mean endpoint exists
    assert response.status_code in [200, 400]


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoints return 404"""
    response = client.get("/invalid/endpoint")
    assert response.status_code == 404

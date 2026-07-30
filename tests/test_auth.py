"""
test_auth.py
------------
Unit/API tests for registration, login, and current-user endpoints.
"""


def test_register_creates_user_and_returns_token(client):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "Secret@123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["role"] == "customer"


def test_register_duplicate_email_fails(client, registered_user):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Jane Again", "email": "jane@example.com", "password": "Secret@123"},
    )
    assert resp.status_code == 400


def test_login_with_correct_credentials(client, registered_user):
    resp = client.post(
        "/api/auth/login", json={"email": "jane@example.com", "password": "Secret@123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_fails(client, registered_user):
    resp = client.post(
        "/api/auth/login", json={"email": "jane@example.com", "password": "WrongPassword"}
    )
    assert resp.status_code == 401


def test_get_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_get_me_with_valid_token(client, registered_user):
    token = registered_user["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "jane@example.com"

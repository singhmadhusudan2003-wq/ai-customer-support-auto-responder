"""
test_integration.py
--------------------
End-to-end integration tests that exercise multiple layers together:
customer registration -> chat -> history -> feedback, and an admin workflow
(promoted directly via the test DB session) -> analytics -> CSV export ->
conversation/user management.
"""

from app.models import UserRole  # noqa: E402


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_full_customer_journey(client, registered_user):
    token = registered_user["access_token"]

    # Send two messages
    r1 = client.post("/api/chat", json={"message": "My headphones stopped working"}, headers=auth_headers(token))
    assert r1.status_code == 200
    msg_id = r1.json()["message_id"]

    r2 = client.post("/api/chat", json={"message": "Also, do you ship internationally?"}, headers=auth_headers(token))
    assert r2.status_code == 200

    # History should show 2 conversations (no conversation_id passed => new each time)
    hist = client.get("/api/history", headers=auth_headers(token))
    assert hist.status_code == 200
    assert len(hist.json()) == 2

    # Suggested questions
    suggestions = client.get("/api/history/suggestions")
    assert suggestions.status_code == 200
    assert len(suggestions.json()) > 0

    # Submit feedback on first AI reply
    fb = client.post(
        "/api/feedback",
        json={"message_id": msg_id, "rating": 1, "comment": "Helpful!"},
        headers=auth_headers(token),
    )
    assert fb.status_code == 201

    # Delete a conversation
    conv_id = hist.json()[0]["id"]
    del_resp = client.delete(f"/api/history/{conv_id}", headers=auth_headers(token))
    assert del_resp.status_code == 200

    hist_after = client.get("/api/history", headers=auth_headers(token))
    assert len(hist_after.json()) == 1


def test_admin_workflow(client, registered_user, monkeypatch):
    from conftest import TestSessionLocal

    # Promote the registered user to admin directly in the test DB
    db = TestSessionLocal()
    from app.models import User

    user = db.query(User).filter(User.email == "jane@example.com").first()
    user.role = UserRole.ADMIN
    db.commit()
    db.close()

    # Re-login to get a fresh token reflecting admin role in the JWT payload
    login = client.post("/api/auth/login", json={"email": "jane@example.com", "password": "Secret@123"})
    admin_token = login.json()["access_token"]

    # Generate some activity as this same (now-admin) user
    client.post("/api/chat", json={"message": "I want a refund immediately!"}, headers=auth_headers(admin_token))

    # Analytics summary
    summary = client.get("/api/analytics/summary", headers=auth_headers(admin_token))
    assert summary.status_code == 200
    assert summary.json()["total_conversations"] >= 1

    # CSV export
    export = client.get("/api/analytics/export/csv", headers=auth_headers(admin_token))
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]

    # Admin conversation listing
    convs = client.get("/api/admin/conversations", headers=auth_headers(admin_token))
    assert convs.status_code == 200
    assert len(convs.json()) >= 1

    # Admin user listing
    users = client.get("/api/admin/users", headers=auth_headers(admin_token))
    assert users.status_code == 200
    assert any(u["email"] == "jane@example.com" for u in users.json())


def test_non_admin_cannot_access_admin_routes(client, registered_user):
    token = registered_user["access_token"]
    resp = client.get("/api/admin/users", headers=auth_headers(token))
    assert resp.status_code == 403

"""
test_chat.py
------------
API tests for the chat pipeline: sending messages, conversation continuity,
predict endpoint, and validation errors.
"""


def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


def test_send_first_message_creates_conversation(client, registered_user):
    resp = client.post(
        "/api/chat",
        json={"message": "What is your return policy?"},
        headers=auth_headers(registered_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["conversation_id"]
    assert data["intent"] in {
        "Complaint", "Refund", "Technical Issue", "Account Issue", "Order Status", "General Inquiry",
    }
    assert data["sentiment"] in {"Positive", "Neutral", "Negative"}
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["escalated"], bool)


def test_follow_up_message_reuses_conversation(client, registered_user):
    first = client.post(
        "/api/chat", json={"message": "Hi there"}, headers=auth_headers(registered_user)
    ).json()
    second = client.post(
        "/api/chat",
        json={"message": "Can you check my order status?", "conversation_id": first["conversation_id"]},
        headers=auth_headers(registered_user),
    ).json()
    assert second["conversation_id"] == first["conversation_id"]


def test_chat_requires_auth(client):
    resp = client.post("/api/chat", json={"message": "Hello"})
    assert resp.status_code == 401


def test_chat_rejects_empty_message(client, registered_user):
    resp = client.post("/api/chat", json={"message": ""}, headers=auth_headers(registered_user))
    assert resp.status_code == 422


def test_predict_endpoint_returns_intent_and_sentiment(client, registered_user):
    resp = client.post(
        "/api/chat/predict",
        json={"text": "I am furious, my order never arrived!"},
        headers=auth_headers(registered_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "intent" in data and "sentiment" in data
    assert 0.0 <= data["intent_confidence"] <= 1.0

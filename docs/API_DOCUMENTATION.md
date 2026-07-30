# API Documentation

Base URL (local dev): `http://localhost:8000`
Interactive Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

All endpoints (except `/`, `/api/health`, `/api/auth/register`, `/api/auth/login`, `/api/history/suggestions`) require a Bearer JWT token:
```
Authorization: Bearer <access_token>
```

---

## Authentication — `/api/auth`

### `POST /api/auth/register`
Create a new customer account.

Request:
```json
{ "name": "Jane Doe", "email": "jane@example.com", "password": "Secret@123" }
```
Response `201`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": "...", "name": "Jane Doe", "email": "jane@example.com", "role": "customer", "is_active": true, "created_at": "..." }
}
```

### `POST /api/auth/login`
```json
{ "email": "jane@example.com", "password": "Secret@123" }
```
Response `200`: same shape as register.

### `GET /api/auth/me`
Returns the current authenticated user.

---

## Chat — `/api/chat`

### `POST /api/chat`
Send a customer message and receive an AI-generated reply.

Request:
```json
{ "message": "I want a refund for my broken headphones", "conversation_id": null }
```
`conversation_id` is optional — omit it to start a new conversation, or pass an existing one to continue it (multi-turn context memory).

Response `200`:
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "reply": "I can help with that. Your refund request has been noted...",
  "intent": "Refund",
  "sentiment": "Negative",
  "confidence": 0.87,
  "escalated": false,
  "response_time_ms": 42.1,
  "sources": ["How do I cancel my order?"]
}
```

### `POST /api/chat/predict`
Lightweight intent + sentiment preview (no reply generation, no DB write).
```json
{ "text": "My account is locked" }
```
Response:
```json
{ "intent": "Account Issue", "intent_confidence": 0.91, "sentiment": "Neutral", "sentiment_confidence": 0.77 }
```

---

## History — `/api/history`

| Method | Path | Description |
|---|---|---|
| GET | `/api/history/suggestions` | Public list of suggested starter questions |
| GET | `/api/history` | List the current user's conversations (summary) |
| GET | `/api/history/{conversation_id}` | Full conversation with all messages |
| DELETE | `/api/history/{conversation_id}` | Delete a conversation (owner only) |

---

## Feedback — `/api/feedback`

### `POST /api/feedback`
```json
{ "message_id": "uuid", "rating": 1, "comment": "Very helpful!" }
```
`rating`: `1` (thumbs up) or `-1` (thumbs down).

---

## Analytics — `/api/analytics`  *(admin only)*

### `GET /api/analytics/summary`
```json
{
  "total_conversations": 152,
  "total_messages": 480,
  "total_customers": 63,
  "escalation_rate": 8.55,
  "avg_response_time_ms": 39.2,
  "avg_confidence": 0.81,
  "intent_breakdown": [{"intent": "Refund", "count": 40}, "..."],
  "sentiment_breakdown": [{"sentiment": "Negative", "count": 55}, "..."],
  "daily_volume": [{"date": "2026-07-01", "count": 12}, "..."]
}
```

### `GET /api/analytics/export/csv`
Streams a CSV file of every message with intent, sentiment, confidence, and timing.

---

## Admin — `/api/admin`  *(admin only)*

| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/conversations` | List every conversation, across all customers |
| GET | `/api/admin/conversations/{id}` | Full transcript of any conversation |
| DELETE | `/api/admin/conversations/{id}` | Delete any conversation |
| GET | `/api/admin/users` | List all users |
| PATCH | `/api/admin/users/{id}` | Update `name`, `is_active`, or `role` |
| DELETE | `/api/admin/users/{id}` | Delete a user (cannot delete yourself) |

---

## Error format

```json
{ "detail": "Human-readable error message" }
```
Common status codes: `400` (bad request), `401` (missing/invalid token), `403` (insufficient permissions), `404` (not found), `422` (validation error).

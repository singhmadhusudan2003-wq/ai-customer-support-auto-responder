"""
schemas.py
----------
Pydantic models (schemas) used for request validation and response
serialization across the API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply: str
    intent: str
    sentiment: str
    confidence: float
    escalated: bool
    response_time_ms: float
    sources: List[str] = []


class MessageOut(BaseModel):
    id: str
    sender: str
    content: str
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    escalated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    escalated: bool
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    escalated: bool
    message_count: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
class FeedbackCreate(BaseModel):
    message_id: str
    rating: int = Field(ge=-1, le=1)
    comment: Optional[str] = None


class FeedbackOut(BaseModel):
    id: str
    message_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
class IntentCount(BaseModel):
    intent: str
    count: int


class SentimentCount(BaseModel):
    sentiment: str
    count: int


class DailyVolume(BaseModel):
    date: str
    count: int


class AnalyticsSummary(BaseModel):
    total_conversations: int
    total_messages: int
    total_customers: int
    escalation_rate: float
    avg_response_time_ms: float
    avg_confidence: float
    intent_breakdown: List[IntentCount]
    sentiment_breakdown: List[SentimentCount]
    daily_volume: List[DailyVolume]


# ---------------------------------------------------------------------------
# Admin - user management
# ---------------------------------------------------------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class PredictResponse(BaseModel):
    intent: str
    intent_confidence: float
    sentiment: str
    sentiment_confidence: float

"""
history.py (router)
---------------------
Conversation history endpoints for the logged-in user: list conversations,
get a single conversation with all messages, delete a conversation, and
fetch suggested starter questions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Conversation, User
from app.schemas import ConversationOut, ConversationSummary

router = APIRouter(prefix="/api/history", tags=["History"])

SUGGESTED_QUESTIONS = [
    "What is your return policy?",
    "How do I track my order?",
    "I want a refund for my last purchase",
    "My device is not turning on, can you help?",
    "How do I reset my account password?",
    "Do you ship internationally?",
]


@router.get("/suggestions", response_model=list)
def get_suggestions():
    return SUGGESTED_QUESTIONS


@router.get("", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return [
        ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            escalated=c.escalated,
            message_count=len(c.messages),
            customer_name=current_user.name,
            customer_email=current_user.email,
        )
        for c in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"detail": "Conversation deleted"}

"""
admin.py (router)
--------------------
Admin-only endpoints: view all conversations across customers, delete any
conversation, and manage users (list, update role/active status, delete).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Conversation, User, UserRole
from app.schemas import ConversationOut, ConversationSummary, UserOut, UserUpdate

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/conversations", response_model=list[ConversationSummary])
def list_all_conversations(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    result = []
    for c in conversations:
        result.append(
            ConversationSummary(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                escalated=c.escalated,
                message_count=len(c.messages),
                customer_name=c.user.name if c.user else None,
                customer_email=c.user.email if c.user else None,
            )
        )
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
def get_any_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_any_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"detail": "Conversation deleted"}


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.name is not None:
        user.name = payload.name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        if payload.role not in (UserRole.ADMIN.value, UserRole.CUSTOMER.value):
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = UserRole(payload.role)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

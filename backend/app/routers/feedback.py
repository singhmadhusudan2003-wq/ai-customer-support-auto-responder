"""
feedback.py (router)
-----------------------
Allows customers to rate individual AI replies (thumbs up / down + optional
comment). Feedback is surfaced in the admin dashboard for quality tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Feedback, Message, User
from app.schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackOut, status_code=201)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = db.query(Message).filter(Message.id == payload.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    feedback = Feedback(message_id=payload.message_id, rating=payload.rating, comment=payload.comment)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

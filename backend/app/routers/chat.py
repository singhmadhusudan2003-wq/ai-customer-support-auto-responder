"""
chat.py (router)
------------------
Core chat endpoint. Handles:
    - Creating/continuing a conversation
    - Storing the customer's message
    - Running the AI pipeline (intent, sentiment, RAG, reply generation)
    - Storing the AI reply with metadata (confidence, escalation, timing)
    - Multi-turn context memory (recent message history is passed to the
      response generator)
"""

import io
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.intent_classifier import intent_classifier
from app.ai.response_generator import generate_response
from app.ai.sentiment_analyzer import sentiment_analyzer
from app.auth import get_current_user
from app.database import get_db
from app.models import Conversation, Message, SenderType, User
from app.schemas import ChatRequest, ChatResponse, PredictRequest, PredictResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    start = time.time()

    # Get or create conversation
    if payload.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == payload.conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        title = payload.message[:50] + ("..." if len(payload.message) > 50 else "")
        conversation = Conversation(user_id=current_user.id, title=title or "New Conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save customer message
    user_message = Message(
        conversation_id=conversation.id,
        sender=SenderType.USER,
        content=payload.message,
    )
    db.add(user_message)
    db.commit()

    # Build recent history for context memory (multi-turn)
    recent_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history = [
        {"sender": m.sender.value, "content": m.content} for m in reversed(recent_messages)
    ]

    # Run AI pipeline
    result = generate_response(payload.message, history=history)
    response_time_ms = round((time.time() - start) * 1000, 2)

    ai_message = Message(
        conversation_id=conversation.id,
        sender=SenderType.AI,
        content=result.reply,
        intent=result.intent,
        sentiment=result.sentiment,
        confidence=result.confidence,
        response_time_ms=response_time_ms,
        escalated=result.escalated,
    )
    db.add(ai_message)

    if result.escalated:
        conversation.escalated = True

    db.commit()
    db.refresh(ai_message)

    logger.info(
        f"Chat | user={current_user.email} | intent={result.intent} | "
        f"sentiment={result.sentiment} | confidence={result.confidence} | escalated={result.escalated}"
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=ai_message.id,
        reply=result.reply,
        intent=result.intent,
        sentiment=result.sentiment,
        confidence=result.confidence,
        escalated=result.escalated,
        response_time_ms=response_time_ms,
        sources=result.sources,
    )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Extracts text from an uploaded PDF or TXT file so the customer can
    attach document context (e.g. an invoice or error log) to their query."""
    filename = (file.filename or "").lower()
    content = await file.read()

    if filename.endswith(".txt"):
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read text file")
    elif filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Could not read PDF file: {exc}")
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    text = text.strip()
    max_chars = 4000
    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars]

    return {
        "filename": file.filename,
        "extracted_text": text,
        "truncated": truncated,
    }


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, current_user: User = Depends(get_current_user)):
    """Lightweight endpoint to preview intent + sentiment predictions only
    (used e.g. by the admin dashboard's classifier playground)."""
    intent, intent_conf = intent_classifier.predict(payload.text)
    sentiment, sentiment_conf = sentiment_analyzer.predict(payload.text)
    return PredictResponse(
        intent=intent,
        intent_confidence=intent_conf,
        sentiment=sentiment,
        sentiment_confidence=sentiment_conf,
    )

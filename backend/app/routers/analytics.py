"""
analytics.py (router)
-----------------------
Admin-only analytics endpoints: overall summary stats, intent/sentiment
breakdowns, daily volume trend, and CSV export of all conversations.
"""

import csv
import io
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Conversation, Message, SenderType, User
from app.schemas import AnalyticsSummary, DailyVolume, IntentCount, SentimentCount

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
    total_messages = db.query(func.count(Message.id)).scalar() or 0
    total_customers = db.query(func.count(func.distinct(Conversation.user_id))).scalar() or 0

    escalated_count = db.query(func.count(Conversation.id)).filter(Conversation.escalated.is_(True)).scalar() or 0
    escalation_rate = round((escalated_count / total_conversations) * 100, 2) if total_conversations else 0.0

    ai_messages = db.query(Message).filter(Message.sender == SenderType.AI).all()
    avg_response_time = (
        round(sum(m.response_time_ms or 0 for m in ai_messages) / len(ai_messages), 2)
        if ai_messages else 0.0
    )
    avg_confidence = (
        round(sum(m.confidence or 0 for m in ai_messages) / len(ai_messages), 4)
        if ai_messages else 0.0
    )

    intent_counter = Counter(m.intent for m in ai_messages if m.intent)
    sentiment_counter = Counter(m.sentiment for m in ai_messages if m.sentiment)

    daily_counter: Counter = Counter()
    for m in ai_messages:
        day = m.created_at.strftime("%Y-%m-%d") if m.created_at else "unknown"
        daily_counter[day] += 1
    daily_volume = [DailyVolume(date=d, count=c) for d, c in sorted(daily_counter.items())]

    return AnalyticsSummary(
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_customers=total_customers,
        escalation_rate=escalation_rate,
        avg_response_time_ms=avg_response_time,
        avg_confidence=avg_confidence,
        intent_breakdown=[IntentCount(intent=k, count=v) for k, v in intent_counter.items()],
        sentiment_breakdown=[SentimentCount(sentiment=k, count=v) for k, v in sentiment_counter.items()],
        daily_volume=daily_volume,
    )


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    messages = (
        db.query(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "message_id", "conversation_id", "sender", "content", "intent",
        "sentiment", "confidence", "response_time_ms", "escalated", "created_at",
    ])
    for m in messages:
        writer.writerow([
            m.id, m.conversation_id, m.sender.value, m.content, m.intent or "",
            m.sentiment or "", m.confidence or "", m.response_time_ms or "",
            m.escalated, m.created_at.isoformat() if m.created_at else "",
        ])
    buffer.seek(0)

    filename = f"conversations_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

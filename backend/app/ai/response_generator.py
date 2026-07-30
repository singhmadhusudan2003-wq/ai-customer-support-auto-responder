"""
response_generator.py
-----------------------
Orchestrates the full auto-responder pipeline:

    1. Intent classification
    2. Sentiment analysis
    3. FAQ retrieval (RAG) for grounding
    4. Reply generation:
         - If USE_OPENAI or USE_OLLAMA is enabled, calls the corresponding
           LLM with the retrieved context for a natural, generated reply.
         - Otherwise, falls back to a template-based reply keyed on intent
           (and RAG answer if a relevant FAQ was found) -- this keeps the
           project fully runnable offline / without any API keys.
    5. Confidence scoring and low-confidence escalation to a human agent.

Multi-turn context memory is handled by the caller (chat router), which
passes the recent conversation history in `history`.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import httpx

from app.ai.intent_classifier import intent_classifier
from app.ai.rag_engine import rag_engine
from app.ai.sentiment_analyzer import sentiment_analyzer
from app.config import settings
from app.utils.logger import logger

TEMPLATE_REPLIES = {
    "Complaint": "I'm really sorry to hear about the trouble you've experienced. I've logged this complaint and our support team will follow up within 24 hours to make it right.",
    "Refund": "I can help with that. Your refund request has been noted -- refunds are typically processed within 5-7 business days back to your original payment method.",
    "Technical Issue": "Sorry for the inconvenience. Let's troubleshoot: please try restarting the device and checking for the latest firmware update. If the issue continues, I'll escalate this to our technical team.",
    "Account Issue": "I understand how important account access is. I've flagged this for our account security team, and you should regain access shortly. In the meantime, you can try the 'Forgot Password' link.",
    "Order Status": "Thanks for checking in! I can see your order is being processed. You'll receive tracking details by email as soon as it ships.",
    "General Inquiry": "Happy to help with that!",
}


@dataclass
class GeneratedReply:
    reply: str
    intent: str
    sentiment: str
    confidence: float
    escalated: bool
    sources: List[str] = field(default_factory=list)


def _template_reply(intent: str, faq_matches: list) -> str:
    base = TEMPLATE_REPLIES.get(intent, TEMPLATE_REPLIES["General Inquiry"])
    if faq_matches:
        best_answer = faq_matches[0][1]
        return f"{base} {best_answer}"
    return base


def _call_openai(prompt: str) -> Optional[str]:
    if not settings.USE_OPENAI or not settings.OPENAI_API_KEY:
        return None
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful, concise customer support agent."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 300,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"OpenAI call failed, falling back to template reply: {exc}")
        return None


def _call_ollama(prompt: str) -> Optional[str]:
    if not settings.USE_OLLAMA:
        return None
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Ollama call failed, falling back to template reply: {exc}")
        return None


def generate_response(message: str, history: Optional[List[dict]] = None) -> GeneratedReply:
    history = history or []

    intent, intent_conf = intent_classifier.predict(message)
    sentiment, sentiment_conf = sentiment_analyzer.predict(message)
    faq_matches = rag_engine.retrieve(message, top_k=2)
    sources = [q for q, _, _ in faq_matches]

    overall_confidence = round((intent_conf + sentiment_conf) / 2, 4)
    escalated = overall_confidence < settings.CONFIDENCE_ESCALATION_THRESHOLD or sentiment == "Negative" and intent == "Complaint" and overall_confidence < 0.7

    context_snippets = "\n".join(f"- Q: {q}\n  A: {a}" for q, a, _ in faq_matches)
    history_text = "\n".join(f"{h['sender']}: {h['content']}" for h in history[-6:])

    prompt = (
        f"Conversation so far:\n{history_text}\n\n"
        f"Relevant FAQ context:\n{context_snippets}\n\n"
        f"Customer's new message (intent={intent}, sentiment={sentiment}):\n{message}\n\n"
        "Write a short, empathetic, helpful customer support reply."
    )

    reply = _call_openai(prompt) or _call_ollama(prompt) or _template_reply(intent, faq_matches)

    if escalated:
        reply += "\n\nI'm also connecting you with a human support specialist to make sure this gets fully resolved."

    return GeneratedReply(
        reply=reply,
        intent=intent,
        sentiment=sentiment,
        confidence=overall_confidence,
        escalated=escalated,
        sources=sources,
    )

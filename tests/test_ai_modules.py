"""
test_ai_modules.py
--------------------
Pure unit tests for the AI building blocks (no HTTP layer): intent
classification and sentiment analysis on representative inputs.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ai.intent_classifier import intent_classifier  # noqa: E402
from app.ai.sentiment_analyzer import sentiment_analyzer  # noqa: E402

VALID_INTENTS = {
    "Complaint", "Refund", "Technical Issue", "Account Issue", "Order Status", "General Inquiry",
}
VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}


def test_intent_classifier_returns_valid_label_and_confidence():
    intent, confidence = intent_classifier.predict("I want a refund for my broken headphones")
    assert intent in VALID_INTENTS
    assert 0.0 <= confidence <= 1.0


def test_intent_classifier_refund_example():
    intent, _ = intent_classifier.predict("Please refund my money for order ORD123456")
    assert intent == "Refund"


def test_sentiment_analyzer_returns_valid_label_and_confidence():
    sentiment, confidence = sentiment_analyzer.predict("This product is amazing, thank you!")
    assert sentiment in VALID_SENTIMENTS
    assert 0.0 <= confidence <= 1.0


def test_sentiment_analyzer_negative_example():
    sentiment, _ = sentiment_analyzer.predict("This is absolutely terrible and I am furious")
    assert sentiment == "Negative"

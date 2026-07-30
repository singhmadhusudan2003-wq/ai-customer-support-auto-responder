"""
intent_classifier.py
---------------------
Loads the trained TF-IDF + Logistic Regression intent classification model
(models/saved/intent_*.pkl) and exposes a simple predict() API returning the
predicted intent class and confidence score.

Falls back to a lightweight keyword-rule classifier if the trained model
artifacts are not found (e.g. before `python models/train_logistic_regression.py`
has been run), so the app always starts successfully.
"""

from pathlib import Path
from typing import Tuple

import joblib

from app.config import settings
from app.utils.logger import logger

MODELS_DIR = Path(settings.MODELS_DIR)

_INTENT_KEYWORDS = {
    "Refund": ["refund", "money back", "reimburse"],
    "Complaint": ["complain", "disappointed", "furious", "worst", "unacceptable", "terrible"],
    "Technical Issue": ["not working", "crash", "error", "won't turn on", "bug", "sync", "reset", "firmware"],
    "Account Issue": ["account", "password", "login", "log in", "locked out"],
    "Order Status": ["order", "delivery", "shipped", "tracking", "delayed"],
}


class IntentClassifier:
    def __init__(self) -> None:
        self.model = None
        self.vectorizer = None
        self.encoder = None
        self._load()

    def _load(self) -> None:
        try:
            self.vectorizer = joblib.load(MODELS_DIR / "intent_vectorizer.pkl")
            self.model = joblib.load(MODELS_DIR / "intent_model.pkl")
            self.encoder = joblib.load(MODELS_DIR / "intent_label_encoder.pkl")
            logger.info("Intent classifier loaded (TF-IDF + Logistic Regression).")
        except FileNotFoundError:
            logger.warning(
                "Trained intent model not found -- falling back to rule-based classifier. "
                "Run `python models/train_logistic_regression.py` to train the real model."
            )

    def predict(self, text: str) -> Tuple[str, float]:
        if self.model is not None:
            vec = self.vectorizer.transform([text])
            probs = self.model.predict_proba(vec)[0]
            idx = probs.argmax()
            intent = self.encoder.inverse_transform([idx])[0]
            confidence = float(probs[idx])
            return intent, confidence

        # --- Rule-based fallback ---
        lowered = text.lower()
        for intent, keywords in _INTENT_KEYWORDS.items():
            if any(kw in lowered for kw in keywords):
                return intent, 0.6
        return "General Inquiry", 0.5


intent_classifier = IntentClassifier()

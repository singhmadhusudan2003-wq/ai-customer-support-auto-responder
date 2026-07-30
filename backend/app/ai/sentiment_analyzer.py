"""
sentiment_analyzer.py
----------------------
Loads the trained TF-IDF + Logistic Regression sentiment model
(models/saved/sentiment_*.pkl) and exposes predict().

Falls back to a small lexicon-based rule classifier if trained artifacts
are missing.
"""

from pathlib import Path
from typing import Tuple

import joblib

from app.config import settings
from app.utils.logger import logger

MODELS_DIR = Path(settings.MODELS_DIR)

_NEGATIVE_WORDS = [
    "furious", "terrible", "worst", "disappointed", "unacceptable", "frustrat",
    "angry", "awful", "bad", "hate", "broken", "damaged", "ignore",
]
_POSITIVE_WORDS = [
    "love", "great", "amazing", "thanks", "thank you", "excellent", "happy", "good",
]


class SentimentAnalyzer:
    def __init__(self) -> None:
        self.model = None
        self.vectorizer = None
        self.encoder = None
        self._load()

    def _load(self) -> None:
        try:
            self.vectorizer = joblib.load(MODELS_DIR / "sentiment_vectorizer.pkl")
            self.model = joblib.load(MODELS_DIR / "sentiment_model.pkl")
            self.encoder = joblib.load(MODELS_DIR / "sentiment_label_encoder.pkl")
            logger.info("Sentiment analyzer loaded (TF-IDF + Logistic Regression).")
        except FileNotFoundError:
            logger.warning(
                "Trained sentiment model not found -- falling back to lexicon-based classifier. "
                "Run `python models/train_logistic_regression.py` to train the real model."
            )

    def predict(self, text: str) -> Tuple[str, float]:
        if self.model is not None:
            vec = self.vectorizer.transform([text])
            probs = self.model.predict_proba(vec)[0]
            idx = probs.argmax()
            sentiment = self.encoder.inverse_transform([idx])[0]
            confidence = float(probs[idx])
            return sentiment, confidence

        # --- Rule-based fallback ---
        lowered = text.lower()
        if any(w in lowered for w in _NEGATIVE_WORDS):
            return "Negative", 0.6
        if any(w in lowered for w in _POSITIVE_WORDS):
            return "Positive", 0.6
        return "Neutral", 0.55


sentiment_analyzer = SentimentAnalyzer()

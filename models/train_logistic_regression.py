"""
train_logistic_regression.py
-----------------------------
Trains TF-IDF + Logistic Regression classifiers for:
    1) Intent classification  (6 classes)
    2) Sentiment analysis     (3 classes)

This is the lightweight, production model used by the live FastAPI backend
for real-time inference (no GPU required, <50ms latency).

Saves:
    models/saved/intent_vectorizer.pkl
    models/saved/intent_model.pkl
    models/saved/intent_label_encoder.pkl
    models/saved/sentiment_vectorizer.pkl
    models/saved/sentiment_model.pkl
    models/saved/sentiment_label_encoder.pkl
    models/saved/metrics_logistic_regression.json

Run:
    python train_logistic_regression.py
"""

import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR.parent / "dataset" / "customer_support_dataset.csv"
SAVE_DIR = BASE_DIR / "saved"
SAVE_DIR.mkdir(exist_ok=True)


def train_classifier(df: pd.DataFrame, target_col: str, name: str) -> dict:
    print(f"\n=== Training {name} classifier ===")
    X = df["query"]
    y = df[target_col]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    start = time.time()
    model = LogisticRegression(max_iter=1000, C=5.0, class_weight="balanced")
    model.fit(X_train_vec, y_train)
    train_time = time.time() - start

    y_pred = model.predict(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(
        y_test, y_pred, target_names=encoder.classes_, output_dict=True, zero_division=0
    )

    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Train time: {train_time:.2f}s")

    joblib.dump(vectorizer, SAVE_DIR / f"{name}_vectorizer.pkl")
    joblib.dump(model, SAVE_DIR / f"{name}_model.pkl")
    joblib.dump(encoder, SAVE_DIR / f"{name}_label_encoder.pkl")

    return {
        "model": "LogisticRegression",
        "target": name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm,
        "labels": encoder.classes_.tolist(),
        "classification_report": report,
        "train_time_seconds": train_time,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }


def main():
    print(f"Loading dataset from {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["query", "intent", "sentiment"])
    print(f"Loaded {len(df)} rows")

    intent_metrics = train_classifier(df, "intent", "intent")
    sentiment_metrics = train_classifier(df, "sentiment", "sentiment")

    all_metrics = {"intent": intent_metrics, "sentiment": sentiment_metrics}
    with open(SAVE_DIR / "metrics_logistic_regression.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\nAll models saved to {SAVE_DIR}")


if __name__ == "__main__":
    main()

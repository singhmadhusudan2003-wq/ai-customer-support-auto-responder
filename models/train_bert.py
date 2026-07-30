"""
train_bert.py
-------------
Fine-tunes `bert-base-uncased` on the intent classification task
using HuggingFace Transformers.

NOTE: This is a heavier, GPU-recommended training job (can take from a few
minutes on a GPU to well over an hour on CPU depending on hardware). It is
NOT run automatically as part of project setup -- the app ships with a fast
TF-IDF + Logistic Regression model (see train_logistic_regression.py) for
real-time inference. Run this script separately when you want to fine-tune
and benchmark a transformer model:

    python train_bert.py

Saves the fine-tuned model + tokenizer to models/saved/bert_intent/
and appends its metrics to models/saved/metrics_bert.json
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset
from transformers import (
    BertForSequenceClassification,
    BertTokenizerFast,
    Trainer,
    TrainingArguments,
)

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR.parent / "dataset" / "customer_support_dataset.csv"
SAVE_DIR = BASE_DIR / "saved" / "bert_intent"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_NAME = "bert-base-uncased"


class QueryDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": precision_score(labels, preds, average="weighted", zero_division=0),
        "recall": recall_score(labels, preds, average="weighted", zero_division=0),
        "f1": f1_score(labels, preds, average="weighted", zero_division=0),
    }


def main():
    df = pd.read_csv(DATASET_PATH).dropna(subset=["query", "intent"])
    encoder = LabelEncoder()
    labels = encoder.fit_transform(df["intent"])

    X_train, X_test, y_train, y_test = train_test_split(
        df["query"].tolist(), labels, test_size=0.2, random_state=42, stratify=labels
    )

    tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
    train_enc = tokenizer(X_train, truncation=True, padding=True, max_length=64)
    test_enc = tokenizer(X_test, truncation=True, padding=True, max_length=64)

    train_dataset = QueryDataset(train_enc, y_train)
    test_dataset = QueryDataset(test_enc, y_test)

    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=len(encoder.classes_)
    )

    training_args = TrainingArguments(
        output_dir=str(SAVE_DIR / "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )

    start = time.time()
    trainer.train()
    train_time = time.time() - start

    eval_results = trainer.evaluate()
    preds = np.argmax(trainer.predict(test_dataset).predictions, axis=-1)
    cm = confusion_matrix(y_test, preds).tolist()

    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)
    import joblib
    joblib.dump(encoder, SAVE_DIR / "label_encoder.pkl")

    metrics = {
        "model": "BERT",
        "target": "intent",
        **eval_results,
        "confusion_matrix": cm,
        "labels": encoder.classes_.tolist(),
        "train_time_seconds": train_time,
    }
    with open(BASE_DIR / "saved" / "metrics_bert.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("BERT training complete. Metrics saved.")


if __name__ == "__main__":
    main()

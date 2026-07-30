"""
compare_models.py
------------------
Aggregates metrics from all trained models (Logistic Regression, DistilBERT,
BERT -- whichever have been trained/saved) into a single comparison table
and bar chart.

Run:
    python compare_models.py
"""
import json
from pathlib import Path

import pandas as pd

SAVE_DIR = Path(__file__).parent / "saved"


def load_metrics():
    rows = []

    lr_path = SAVE_DIR / "metrics_logistic_regression.json"
    if lr_path.exists():
        data = json.load(open(lr_path))
        for target, m in data.items():
            rows.append({
                "model": "Logistic Regression",
                "task": target,
                "accuracy": m["accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1_score": m["f1_score"],
            })

    for name, label in [("metrics_distilbert.json", "DistilBERT"), ("metrics_bert.json", "BERT")]:
        p = SAVE_DIR / name
        if p.exists():
            m = json.load(open(p))
            rows.append({
                "model": label,
                "task": m.get("target", "intent"),
                "accuracy": m.get("eval_accuracy", m.get("accuracy")),
                "precision": m.get("eval_precision", m.get("precision")),
                "recall": m.get("eval_recall", m.get("recall")),
                "f1_score": m.get("eval_f1", m.get("f1_score")),
            })

    return pd.DataFrame(rows)


def main():
    df = load_metrics()
    if df.empty:
        print("No trained model metrics found. Run train_logistic_regression.py first.")
        return
    print("\n=== Model Comparison ===\n")
    print(df.to_string(index=False))
    out_path = SAVE_DIR / "model_comparison.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved comparison table -> {out_path}")


if __name__ == "__main__":
    main()

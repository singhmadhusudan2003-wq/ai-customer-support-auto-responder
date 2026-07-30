"""
rag_engine.py
--------------
Retrieval-Augmented Generation engine for FAQ lookup.

Embeds the FAQ knowledge base (dataset/faq.csv) with a SentenceTransformer
model and indexes it with FAISS for fast approximate-nearest-neighbour
retrieval. Given a customer query, retrieves the top-k most relevant FAQ
entries to ground the auto-generated reply and provide "sources".

Gracefully degrades to a TF-IDF cosine-similarity retriever if the
sentence-transformers model cannot be downloaded/loaded (e.g. no internet
access in an offline/air-gapped environment), so the app never crashes.
"""

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

from app.config import settings
from app.utils.logger import logger

FAQ_PATH = Path(settings.DATASET_DIR) / "faq.csv"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class RAGEngine:
    def __init__(self) -> None:
        self.faq_df = pd.DataFrame(columns=["question", "answer"])
        self.mode = "none"  # "sentence-transformers" | "tfidf" | "none"
        self.embedder = None
        self.index = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self._load_faq()
        self._build_index()

    def _load_faq(self) -> None:
        if FAQ_PATH.exists():
            self.faq_df = pd.read_csv(FAQ_PATH)
            logger.info(f"Loaded {len(self.faq_df)} FAQ entries from {FAQ_PATH}")
        else:
            logger.warning(f"FAQ file not found at {FAQ_PATH}; RAG retrieval disabled.")

    def _build_index(self) -> None:
        if self.faq_df.empty:
            return

        questions = self.faq_df["question"].tolist()

        # --- Preferred: SentenceTransformers + FAISS ---
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
            embeddings = self.embedder.encode(questions, normalize_embeddings=True)
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(np.array(embeddings, dtype="float32"))
            self.mode = "sentence-transformers"
            logger.info("RAG engine using SentenceTransformer + FAISS.")
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Falling back to TF-IDF retrieval for RAG (reason: {exc})")

        # --- Fallback: TF-IDF cosine similarity ---
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(questions)
            self.mode = "tfidf"
            logger.info("RAG engine using TF-IDF cosine similarity fallback.")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"RAG engine could not be initialized: {exc}")
            self.mode = "none"

    def retrieve(self, query: str, top_k: int = 2, min_score: float = 0.35) -> List[Tuple[str, str, float]]:
        """Returns list of (question, answer, score) tuples above min_score."""
        if self.faq_df.empty or self.mode == "none":
            return []

        if self.mode == "sentence-transformers":
            query_vec = self.embedder.encode([query], normalize_embeddings=True)
            scores, idxs = self.index.search(np.array(query_vec, dtype="float32"), top_k)
            results = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx == -1 or score < min_score:
                    continue
                row = self.faq_df.iloc[idx]
                results.append((row["question"], row["answer"], float(score)))
            return results

        if self.mode == "tfidf":
            from sklearn.metrics.pairwise import cosine_similarity

            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            top_idxs = sims.argsort()[::-1][:top_k]
            results = []
            for idx in top_idxs:
                if sims[idx] < min_score:
                    continue
                row = self.faq_df.iloc[idx]
                results.append((row["question"], row["answer"], float(sims[idx])))
            return results

        return []


rag_engine = RAGEngine()

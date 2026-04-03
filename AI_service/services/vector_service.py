"""
Vector Service
Embeds text chunks using sentence-transformers (all-MiniLM-L6-v2)
and stores them in an in-memory FAISS index for fast retrieval.
Model is downloaded once (~90MB) on first use.
"""

import os
import logging
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Singleton model — loaded once, reused across requests
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


class VectorStore:
    """
    In-memory FAISS vector store for a single request lifecycle.
    Stores chunks and their embeddings for semantic retrieval.
    """

    def __init__(self):
        self.chunks: list[str] = []
        self.index: faiss.IndexFlatL2 | None = None
        self.dimension: int = 0

    def build(self, chunks: list[str]) -> None:
        """Embed all chunks and build the FAISS index."""
        if not chunks:
            raise ValueError("Cannot build vector store from empty chunk list.")

        model = get_embedding_model()

        logger.info(f"Embedding {len(chunks)} chunks...")
        embeddings = model.encode(chunks, show_progress_bar=False, batch_size=32)
        embeddings = np.array(embeddings, dtype=np.float32)

        self.dimension = embeddings.shape[1]
        self.chunks = chunks

        # Use L2 flat index (exact search, fast for small datasets)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        logger.info(f"FAISS index built: {self.index.ntotal} vectors, dim={self.dimension}")

    def retrieve(self, query: str, k: int = 5) -> list[str]:
        """
        Retrieve top-k most relevant chunks for a given query.
        Returns list of chunk strings.
        """
        if self.index is None or self.index.ntotal == 0:
            raise RuntimeError("Vector store is empty. Call build() first.")

        k = min(k, len(self.chunks))
        model = get_embedding_model()

        query_embedding = model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding, dtype=np.float32)

        distances, indices = self.index.search(query_embedding, k)
        retrieved = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

        logger.debug(f"Retrieved {len(retrieved)} chunks for query: '{query[:60]}...'")
        return retrieved

    def get_overview_chunks(self, n: int = 6) -> list[str]:
        """Return first n chunks (beginning of video = intro/overview)."""
        return self.chunks[:n]

    def get_all_text(self) -> str:
        """Return full concatenated transcript (for short videos)."""
        return " ".join(self.chunks)

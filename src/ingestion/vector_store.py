import pickle
from pathlib import Path
from typing import List

import faiss
import numpy as np
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL_NAME,
    VECTOR_INDEX_PATH,
    VECTOR_METADATA_PATH,
    VECTOR_STORE_DIR,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    FAISS-backed vector store for semantic retrieval.

    Design choice:
    - ONLY policy documents are indexed
    - Noise documents are excluded at ingestion time
    """

    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index: faiss.IndexFlatIP | None = None
        self.documents: List[Document] = []

    def _ensure_index(self, embedding_dim: int) -> None:
        if self.index is None:
            self.index = faiss.IndexFlatIP(embedding_dim)

    def _embed_documents(self, documents: List[Document]) -> np.ndarray:
        texts = [doc.page_content for doc in documents]
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.astype("float32")

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.

        IMPORTANT:
        - Filters out non-policy documents
        """
        policy_docs = [
            doc for doc in documents if doc.metadata.get("is_policy") is True
        ]

        if not policy_docs:
            logger.warning("No policy documents to index")
            return

        embeddings = self._embed_documents(policy_docs)
        self._ensure_index(embeddings.shape[1])
        assert self.index is not None

        self.index.add(embeddings)
        self.documents.extend(policy_docs)
        self._persist()

        logger.info(
            "Indexed policy documents",
            extra={"count": len(policy_docs)},
        )

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Perform semantic similarity search over policy documents.
        """
        if self.index is None or not self.documents:
            self._load()

        if self.index is None or not self.documents:
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        _, indices = self.index.search(query_embedding, k)

        return [
            self.documents[idx]
            for idx in indices[0]
            if idx != -1
        ]

    def rebuild_index(self, documents: List[Document]) -> None:
        """
        Rebuild index from scratch (used after new uploads).
        """
        self.index = None
        self.documents = []
        self.add_documents(documents)

    def _persist(self) -> None:
        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        if self.index is None:
            return

        faiss.write_index(self.index, str(VECTOR_INDEX_PATH))
        with VECTOR_METADATA_PATH.open("wb") as f:
            pickle.dump(self.documents, f)

        logger.info("Persisted vector store", extra={"documents": len(self.documents)})

    def _load(self) -> None:
        if not VECTOR_INDEX_PATH.exists() or not VECTOR_METADATA_PATH.exists():
            return

        self.index = faiss.read_index(str(VECTOR_INDEX_PATH))
        with VECTOR_METADATA_PATH.open("rb") as f:
            self.documents = pickle.load(f)

        logger.info("Loaded vector store", extra={"documents": len(self.documents)})

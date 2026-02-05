from typing import List

from langchain_core.documents import Document

from src.ingestion.vector_store import VectorStore
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PolicyRetriever:
    """
    Responsible for retrieving candidate documents relevant to a user query.

    Design principles:
    - Pure retrieval logic (no business rules)
    - Returns potentially noisy results
    - Precision is improved downstream via reranking and conflict resolution
    """

    def __init__(self, vector_store: VectorStore, top_k: int = 5) -> None:
        """
        Args:
            vector_store: FAISS-backed vector store instance
            top_k: Number of candidate documents to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieve top-k semantically similar documents for the given query.

        Note:
        - Retrieval is recall-oriented
        - Noise filtering and policy resolution happen later
        """
        if not query.strip():
            logger.warning("Empty query received by retriever")
            return []

        documents = self.vector_store.similarity_search(
            query=query,
            k=self.top_k,
        )

        logger.info(
            "Retrieved candidate documents",
            extra={
                "query": query,
                "count": len(documents),
                "sources": [doc.metadata.get("source") for doc in documents],
            },
        )

        return documents
from datetime import datetime
from typing import List

from langchain_core.documents import Document

from src.constants import DOC_TYPE_POLICY
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentReranker:
    """
    Reranks retrieved documents using domain-specific heuristics.

    Why this exists:
    - Vector similarity alone is insufficient
    - We want newer policies ranked above older ones
    - Noise documents should be strongly penalized
    """

    def rerank(self, documents: List[Document]) -> List[Document]:
        """
        Rerank documents based on custom scoring logic.

        Returns:
            Documents sorted by descending relevance score
        """
        if not documents:
            return []

        scored_docs = [(self._score(doc), doc) for doc in documents]
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        reranked = [doc for _, doc in scored_docs]

        logger.info(
            "Reranked documents",
            extra={
                "order": [
                    {
                        "source": doc.metadata.get("source"),
                        "score": self._score(doc),
                    }
                    for doc in reranked
                ]
            },
        )

        return reranked

    def _score(self, document: Document) -> float:
        """
        Compute a relevance score for a document.

        Scoring logic:
        - Strong boost for policy documents
        - Massive penalty for non-policy (noise)
        - Newer policies score higher than older ones
        """
        score = 0.0

        doc_type = document.metadata.get("doc_type")

        # Authoritative policy documents get priority
        if doc_type == DOC_TYPE_POLICY:
            score += 10.0
        else:
            # Hard penalty to push noise to the bottom
            score -= 100.0

        # Prefer newer policies over older ones
        effective_date: datetime | None = document.metadata.get("effective_date")
        if effective_date:
            score += effective_date.timestamp() / 1e11

        return score
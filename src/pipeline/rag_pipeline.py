from typing import Dict, List

from langchain_core.documents import Document

# Ingestion layer
from src.ingestion.document_loader import load_documents
from src.ingestion.metadata_extractor import enrich_documents
from src.ingestion.vector_store import VectorStore

# Retrieval & reasoning layers
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import DocumentReranker
from src.retrieval.conflict_resolver import resolve_conflicts

# Generation layer
from src.generation.answer_generator import generate_answer

# Logging utility
from src.utils.logging import get_logger

from src.config import DEBUG_RAG

logger = get_logger(__name__)


class RagPipeline:
    """
    End-to-end Retrieval-Augmented Generation (RAG) pipeline.

    Responsibilities:
    - Manage vector store lifecycle
    - Orchestrate retrieval, reranking, and conflict resolution
    - Generate a final, source-cited answer

    Design principle:
    Each stage has a single responsibility and can be tested independently.
    """

    def __init__(self) -> None:
        """
        Initialize core pipeline components.

        Notes:
        - VectorStore handles embeddings + FAISS index
        - Retriever performs recall-oriented semantic search
        """
        self.vector_store = VectorStore()
        self.retriever = PolicyRetriever(self.vector_store)
        self.reranker = DocumentReranker()

    def rebuild(self) -> None:
        """
        Rebuild the entire vector index from the knowledge base.

        Use cases:
        - First-time startup
        - After uploading new documents
        - When embeddings or metadata logic changes

        Steps:
        1. Load raw documents from disk
        2. Enrich with metadata (policy vs noise, dates, etc.)
        3. Rebuild FAISS index using policy documents only
        """
        docs = enrich_documents(load_documents())
        self.vector_store.rebuild_index(docs)

        logger.info(
            "Pipeline rebuild complete",
            extra={"documents": len(docs)},
        )

    def answer_question(self, query: str) -> Dict[str, List[str] | str]:
        """
        Answer a user question using the RAG pipeline.

        Pipeline stages:
        1. Retrieve candidate documents (recall-focused)
        2. Rerank documents using domain heuristics
        3. Resolve conflicts and remove noise
        4. Generate an answer using the final authoritative context

        Returns:
            {
                "answer": str,
                "sources": List[str]
            }
        """
        logger.info("Answering question", extra={"query": query})

        # Step 1: Retrieve semantically similar documents
        retrieved_docs = self.retriever.retrieve(query)

        # Step 2: Rerank using policy priority and recency
        reranked_docs = self.reranker.rerank(retrieved_docs)

        # Step 3: Resolve conflicts (keep latest policy, drop noise)
        resolved_docs = resolve_conflicts(reranked_docs)

        # Collect source filenames for citation
        sources = [doc.metadata.get("source", "") for doc in resolved_docs]

        # Guardrail: no authoritative documents found
        if not resolved_docs:
            logger.warning("No authoritative documents found for query")
            return {
                "answer": "I do not know based on the provided context.\nSources: none",
                "sources": [],
            }
        # RAG contract: only authoritative policy docs may reach generation
        assert all(
            doc.metadata.get("doc_type") == "policy"
            for doc in resolved_docs
        ), "RAG contract violated: non-policy document reached generation"

        # Step 4: Generate final answer using LLM
        answer = generate_answer(query, resolved_docs)

        # Enforce citation format if LLM forgot to include it
        sources_line = ", ".join(s for s in sources if s)
        if "Sources:" not in answer:
            answer = f"{answer}\nSources: {sources_line}"

        if DEBUG_RAG:
            logger.info(
                "RAG retrieval",
                extra={"sources": [d.metadata["source"] for d in retrieved_docs]},
            )

            logger.info(
                "RAG rerank",
                extra={"sources": [d.metadata["source"] for d in reranked_docs]},
            )

            logger.info(
                "RAG resolved",
                extra={"sources": [d.metadata["source"] for d in resolved_docs]},
            )

        logger.info(
            "Answer justification",
            extra={
                "policy_used": resolved_docs[0].metadata.get("source"),
                "effective_date": resolved_docs[0].metadata.get("effective_date"),
            },
        )

        return {
            "answer": answer,
            "sources": sources,
        }
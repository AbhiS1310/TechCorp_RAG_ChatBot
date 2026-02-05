from pathlib import Path
from typing import List

from langchain_core.documents import Document

from src.config import KNOWLEDGE_BASE_DIR
from src.utils.logging import get_logger

logger = get_logger(__name__)


def load_documents(directory: Path = KNOWLEDGE_BASE_DIR) -> List[Document]:
    """
    Load raw text documents from the knowledge base directory.

    Responsibility:
    - Read .txt files
    - Attach minimal metadata (source filename)
    - DO NOT apply business logic (policy vs noise handled later)
    """
    if not directory.exists():
        logger.warning("Knowledge base directory missing: %s", directory)
        return []

    documents: List[Document] = []

    for file_path in sorted(directory.glob("*.txt")):
        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            logger.error("Failed to read file (encoding issue): %s", file_path.name)
            continue

        if not content:
            logger.warning("Skipping empty file: %s", file_path.name)
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "source_path": str(file_path),
                },
            )
        )

    logger.info("Loaded %s documents from knowledge base", len(documents))
    return documents

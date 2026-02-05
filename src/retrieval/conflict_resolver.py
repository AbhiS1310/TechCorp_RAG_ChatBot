from datetime import datetime
from typing import List

from langchain_core.documents import Document

from src.constants import DOC_TYPE_POLICY
from src.utils.logging import get_logger

logger = get_logger(__name__)


def resolve_conflicts(documents: List[Document]) -> List[Document]:
    """
    Resolve conflicting policy documents by selecting the latest effective policy.
    Noise documents are discarded at this stage.
    """
    policies = [
        doc for doc in documents
        if doc.metadata.get("doc_type") == DOC_TYPE_POLICY
    ]

    if not policies:
        logger.warning("No policy documents found after retrieval")
        return []

    latest_policy = max(
        policies,
        key=lambda d: d.metadata.get("effective_date") or datetime.min,
    )

    logger.info(
        "Resolved policy conflicts",
        extra={
            "selected_policy": latest_policy.metadata.get("source"),
            "effective_date": latest_policy.metadata.get("effective_date"),
        },
    )

    return [latest_policy]

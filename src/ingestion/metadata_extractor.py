import re
from datetime import datetime
from typing import Optional

from langchain_core.documents import Document

from src.constants import DOC_TYPE_NOISE, DOC_TYPE_POLICY

# Matches: "Effective Date: Jan 1, 2024"
DATE_PATTERN = re.compile(
    r"effective\s+date\s*:\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    re.IGNORECASE,
)


def _parse_effective_date(text: str) -> Optional[datetime]:
    """
    Extract and parse an effective date from document text.

    Returns:
        datetime if found, otherwise None
    """
    match = DATE_PATTERN.search(text)
    if not match:
        return None

    raw_date = match.group(1).strip()

    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw_date, fmt)
        except ValueError:
            continue

    return None


def enrich_metadata(document: Document) -> Document:
    """
    Enrich a document with structured metadata used for
    retrieval, filtering, and conflict resolution.
    """
    text = document.page_content
    source = document.metadata.get("source", "").lower()

    # Step 1: Identify document type
    is_policy = "policy" in source
    doc_type = DOC_TYPE_POLICY if is_policy else DOC_TYPE_NOISE

    # Step 2: Extract effective date (policies only)
    effective_date = _parse_effective_date(text) if is_policy else None
    year = effective_date.year if effective_date else None

    # Step 3: Assign policy precedence score
    # Higher = more authoritative
    policy_rank = year if is_policy and year else 0

    document.metadata.update(
        {
            "doc_type": doc_type,
            "is_policy": is_policy,
            "effective_date": effective_date,
            "year": year,
            "policy_rank": policy_rank,
        }
    )

    return document


def enrich_documents(documents: list[Document]) -> list[Document]:
    """
    Apply metadata enrichment to all documents.
    """
    return [enrich_metadata(doc) for doc in documents]

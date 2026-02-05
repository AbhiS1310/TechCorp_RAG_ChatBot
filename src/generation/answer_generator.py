import os
from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from src.config import GROQ_MODEL_NAME
from src.generation.prompt_templates import SYSTEM_PROMPT, USER_PROMPT
from src.utils.logging import get_logger

logger = get_logger(__name__)


def generate_answer(query: str, documents: List[Document]) -> str:
    """
    Generate a natural-language answer to a user query using an LLM,
    grounded strictly in the provided authoritative documents.

    Responsibilities:
    - Construct a constrained prompt using system + user templates
    - Inject retrieved policy context into the prompt
    - Call the Groq-hosted LLM deterministically
    - Return the raw model response (post-processing handled upstream)

    IMPORTANT:
    - This function assumes documents have already been filtered
      to authoritative policy documents only.
    """
    # Combine document contents into a single context block.
    # Documents are already conflict-resolved at this stage.
    context = "\n\n".join([doc.page_content for doc in documents])

    logger.info(
        "Generating answer",
        extra={
            "context_chars": len(context),
            "documents": len(documents),
        },
    )

    # Create a structured chat prompt using system and user messages.
    # The system prompt enforces strict policy-only behavior.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT),
        ]
    )

    # Initialize Groq LLM client.
    # temperature=0 ensures deterministic, non-creative outputs,
    # which is critical for policy accuracy.
    llm = ChatGroq(
        model=GROQ_MODEL_NAME,
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # Render the final message list with injected variables.
    messages = prompt.format_messages(
        question=query,
        context=context,
    )

    # Invoke the LLM synchronously.
    response = llm.invoke(messages)

    logger.info("Generated answer successfully")

    # Return only the textual content of the response.
    # Source enforcement and formatting are handled in the pipeline.
    return response.content
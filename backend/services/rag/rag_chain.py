from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from backend.services.rag.llm_service import (
    create_chat_model,
)
from backend.services.rag.prompt import (
    create_rag_prompt,
)


def create_rag_chain() -> Runnable:
    """
    RAG cevap üretimi için:

    Prompt
      ↓
    LLM
      ↓
    String Output

    zincirini oluşturur.
    """

    prompt = create_rag_prompt()
    model = create_chat_model()
    output_parser = StrOutputParser()

    chain = (
        prompt
        | model
        | output_parser
    )

    return chain
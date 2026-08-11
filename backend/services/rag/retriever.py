from __future__ import annotations

from langchain_core.documents import Document

from backend.services.rag.vector_store import (
    load_vector_store,
)


def retrieve_documents(
    query: str,
    machine_id: str,
    k: int = 5,
) -> list[Document]:
    """
    Verilen sorgu için ilgili makineye ait
    en alakalı knowledge-base chunk'larını getirir.
    """

    if not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    vector_store = load_vector_store()

    documents = vector_store.similarity_search(
        query=query,
        k=k,
        filter={
            "machine_id": machine_id,
        },
    )

    return documents
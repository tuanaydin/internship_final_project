from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.core.config import PROJECT_ROOT
from backend.services.rag.embedding_service import (
    create_embedding_model,
)


VECTOR_STORE_DIR = (
    PROJECT_ROOT / "storage" / "chroma"
)

COLLECTION_NAME = "iot_maintenance_kb"


def create_vector_store(
    chunks: list[Document],
) -> Chroma:
    """
    Chunk'ları embedding'lerini üreterek
    persistent Chroma vector store'a kaydeder.
    """

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    embedding_model = create_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=str(
            VECTOR_STORE_DIR
        ),
        ids=[
            chunk.metadata["chunk_id"]
            for chunk in chunks
        ],
    )

    return vector_store


def load_vector_store() -> Chroma:
    """
    Daha önce oluşturulmuş persistent
    Chroma vector store'u yükler.
    """

    embedding_model = create_embedding_model()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=str(
            VECTOR_STORE_DIR
        ),
    )
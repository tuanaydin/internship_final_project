from __future__ import annotations

from collections import defaultdict

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def create_chunks(
    documents: list[Document],
) -> list[Document]:
    """
    Yüklenen dokümanları retrieval için
    daha küçük parçalara böler.

    Mevcut metadata korunur ve her parçaya
    benzersiz chunk_id eklenir.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        length_function=len,
    )

    chunks = splitter.split_documents(
        documents
    )

    document_counters: dict[str, int] = defaultdict(int)

    for chunk in chunks:
        document_id = chunk.metadata.get(
            "document_id",
            "UNKNOWN",
        )

        chunk_number = document_counters[
            document_id
        ]

        chunk.metadata["chunk_id"] = (
            f"{document_id}"
            f"_CHUNK_{chunk_number:04d}"
        )

        document_counters[document_id] += 1

    return chunks
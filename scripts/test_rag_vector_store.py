from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.chunking_service import (
    create_chunks,
)
from backend.services.rag.document_loader import (
    load_machine_documents,
)
from backend.services.rag.vector_store import (
    create_vector_store,
)


def main() -> None:
    machine_id = "MOTOR_A"

    print("=" * 70)
    print("RAG VECTOR STORE TEST")
    print("=" * 70)

    documents = load_machine_documents(
        machine_id
    )

    chunks = create_chunks(
        documents
    )

    print()
    print(
        f"Chunks to index: {len(chunks)}"
    )

    vector_store = create_vector_store(
        chunks
    )

    print()
    print("✓ Vector store created")

    query = (
        "Titreşim kritik seviyedeyse "
        "hangi bakım işlemleri yapılmalı?"
    )

    print()
    print("Query:")
    print(query)

    results = vector_store.similarity_search(
        query,
        k=5,
        filter={
            "machine_id": machine_id,
        },
    )

    print()
    print("=" * 70)
    print("TOP RESULTS")
    print("=" * 70)

    for index, document in enumerate(
        results,
        start=1,
    ):
        print()
        print(f"[{index}]")

        print(
            "Chunk:",
            document.metadata.get(
                "chunk_id"
            ),
        )

        print(
            "Document:",
            document.metadata.get(
                "document_id"
            ),
        )

        print(
            "Type:",
            document.metadata.get(
                "document_type"
            ),
        )

        print()
        print(document.page_content[:600])

        print("-" * 70)


if __name__ == "__main__":
    main()
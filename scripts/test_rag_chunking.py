from __future__ import annotations

import sys
from collections import Counter
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


def main() -> None:
    machine_id = "MOTOR_A"

    documents = load_machine_documents(
        machine_id
    )

    chunks = create_chunks(
        documents
    )

    print("=" * 70)
    print("RAG CHUNKING TEST")
    print("=" * 70)

    print()
    print(
        f"Original document units: {len(documents)}"
    )
    print(
        f"Generated chunks: {len(chunks)}"
    )

    print()
    print("=" * 70)
    print("CHUNKS PER DOCUMENT")
    print("=" * 70)

    counts = Counter(
        chunk.metadata["document_id"]
        for chunk in chunks
    )

    for document_id, count in counts.items():
        print(
            f"{document_id}: {count}"
        )

    print()
    print("=" * 70)
    print("FIRST 10 CHUNKS")
    print("=" * 70)

    for chunk in chunks[:10]:
        print()
        print(
            "Chunk ID:",
            chunk.metadata.get("chunk_id"),
        )

        print(
            "Document:",
            chunk.metadata.get(
                "document_id"
            ),
        )

        print(
            "Type:",
            chunk.metadata.get(
                "document_type"
            ),
        )

        print(
            "Machine:",
            chunk.metadata.get(
                "machine_id"
            ),
        )

        print(
            "Page:",
            chunk.metadata.get(
                "page_number"
            ),
        )

        print(
            "Length:",
            len(chunk.page_content),
        )

        print()
        print("Content:")
        print(
            chunk.page_content[:500]
        )

        print("-" * 70)

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    if not chunks:
        raise RuntimeError(
            "No chunks were generated."
        )

    chunk_ids = [
        chunk.metadata.get("chunk_id")
        for chunk in chunks
    ]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise RuntimeError(
            "Duplicate chunk_id detected."
        )

    for chunk in chunks:

        if not chunk.page_content.strip():
            raise RuntimeError(
                "Empty chunk detected."
            )

        if not chunk.metadata.get(
            "machine_id"
        ):
            raise RuntimeError(
                "machine_id metadata missing."
            )

        if not chunk.metadata.get(
            "document_id"
        ):
            raise RuntimeError(
                "document_id metadata missing."
            )

    print("✓ Chunks generated")
    print("✓ Chunk IDs are unique")
    print("✓ Asset metadata preserved")
    print("✓ No empty chunks")
    print()
    print(
        "RAG chunking test completed successfully."
    )


if __name__ == "__main__":
    main()
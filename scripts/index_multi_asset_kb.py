from __future__ import annotations

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
    machine_ids = [
        "PUMP_B",
        "VALVE_C",
    ]

    all_chunks = []

    for machine_id in machine_ids:
        documents = load_machine_documents(
            machine_id
        )

        chunks = create_chunks(
            documents
        )

        all_chunks.extend(
            chunks
        )

        print(
            f"{machine_id}: "
            f"{len(documents)} doküman, "
            f"{len(chunks)} chunk hazırlandı."
        )

    if not all_chunks:
        print(
            "Indexlenecek chunk bulunamadı."
        )
        return

    create_vector_store(
        all_chunks
    )

    print()
    print(
        f"Toplam {len(all_chunks)} chunk "
        "Chroma vector store'a eklendi."
    )


if __name__ == "__main__":
    main()
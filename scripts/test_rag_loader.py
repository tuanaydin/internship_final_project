from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.document_loader import (
    load_machine_documents,
)


def main() -> None:
    machine_id = "MOTOR_A"

    print("=" * 70)
    print("RAG DOCUMENT LOADER TEST")
    print("=" * 70)

    documents = load_machine_documents(
        machine_id
    )

    print()
    print(f"Machine: {machine_id}")
    print(
        f"Loaded document units: {len(documents)}"
    )

    if not documents:
        raise RuntimeError(
            "No documents were loaded."
        )

    print()
    print("=" * 70)
    print("LOADED DOCUMENTS")
    print("=" * 70)

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        print()
        print(f"[{index}]")
        print(
            "Document ID:",
            metadata.get("document_id"),
        )
        print(
            "Document Type:",
            metadata.get("document_type"),
        )
        print(
            "Machine:",
            metadata.get("machine_id"),
        )
        print(
            "Station:",
            metadata.get("station_id"),
        )
        print(
            "Plant:",
            metadata.get("plant_id"),
        )
        print(
            "File Type:",
            metadata.get("file_type"),
        )
        print(
            "Page:",
            metadata.get("page_number"),
        )
        print(
            "Source:",
            metadata.get("source"),
        )

        print(
            "Text length:",
            len(document.page_content),
        )

        print()
        print("Text preview:")
        print(
            document.page_content[:300]
        )

        print("-" * 70)

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    required_metadata = {
        "plant_id",
        "station_id",
        "machine_id",
        "document_id",
        "document_type",
        "source",
        "file_type",
        "page_number",
    }

    for document in documents:
        missing_metadata = (
            required_metadata
            - document.metadata.keys()
        )

        if missing_metadata:
            raise RuntimeError(
                "Missing metadata fields: "
                f"{missing_metadata}"
            )

        if not document.page_content.strip():
            raise RuntimeError(
                "Empty document content detected: "
                f"{document.metadata.get('source')}"
            )

    print("✓ Documents loaded")
    print("✓ Content is not empty")
    print("✓ Required metadata exists")
    print()
    print("RAG loader test completed successfully.")


if __name__ == "__main__":
    main()
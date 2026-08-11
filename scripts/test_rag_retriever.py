from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.retriever import (
    retrieve_documents,
)


TEST_QUERIES = [
    "Titreşim kritik seviyedeyse hangi bakım işlemleri yapılmalı?",
    "Motor sıcaklığı artıyor ancak titreşim normal. Olası neden nedir?",
    "Rulman problemiyle ilgili geçmiş benzer bir olay var mı?",
]


def main() -> None:
    machine_id = "MOTOR_A"

    for query in TEST_QUERIES:

        print()
        print("=" * 70)
        print("QUERY")
        print("=" * 70)
        print(query)

        results = retrieve_documents(
            query=query,
            machine_id=machine_id,
            k=5,
        )

        print()
        print("RESULTS")

        for index, document in enumerate(
            results,
            start=1,
        ):
            print()
            print(
                f"[{index}]",
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

            print(
                document.page_content[:500]
            )

            print("-" * 70)


if __name__ == "__main__":
    main()
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.embedding_service import (
    create_embedding_model,
)


def main() -> None:

    print("=" * 70)
    print("RAG EMBEDDING TEST")
    print("=" * 70)

    embedding_model = create_embedding_model()

    text = (
        "Motor titreşimi kritik seviyeye ulaştı."
    )

    vector = embedding_model.embed_query(
        text
    )

    print()
    print("Input:")
    print(text)

    print()
    print(
        "Vector dimension:",
        len(vector),
    )

    print()
    print(
        "First 10 values:"
    )

    print(
        vector[:10]
    )

    if not vector:
        raise RuntimeError(
            "Embedding vector is empty."
        )

    print()
    print("✓ Embedding generated")
    print(
        "RAG embedding test completed successfully."
    )


if __name__ == "__main__":
    main()
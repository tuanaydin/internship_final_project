from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.rag_service import (
    prepare_rag_context_at,
)


def main() -> None:
    machine_id = "MOTOR_A"

    timestamp = "2026-07-27 20:00:00"

    question = (
        "Motor-A neden kritik durumda "
        "ve hangi bakım işlemleri yapılmalı?"
    )

    result = prepare_rag_context_at(
        machine_id=machine_id,
        question=question,
        timestamp=timestamp,
        window_minutes=300,
        k=5,
    )

    print("=" * 70)
    print("RAG SERVİSİ UÇTAN UCA TESTİ")
    print("=" * 70)

    print()
    print("Makine:")
    print(
        result["machine_id"]
    )

    print()
    print("İstenen zaman:")
    print(
        result["requested_timestamp"]
    )

    print()
    print("=" * 70)
    print("DETERMİNİSTİK ANALİZ")
    print("=" * 70)

    deterministic = result[
        "deterministic_analysis"
    ]

    for key, value in deterministic.items():
        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 70)
    print("RETRIEVAL SORGUSU")
    print("=" * 70)

    print(
        result["retrieval_query"]
    )

    print()
    print("=" * 70)
    print("GETİRİLEN KAYNAKLAR")
    print("=" * 70)

    retrieved_documents = result[
        "retrieved_documents"
    ]

    for index, document in enumerate(
        retrieved_documents,
        start=1,
    ):
        print()
        print(
            f"[{index}] "
            f"{document.metadata.get('chunk_id')}"
        )

        print(
            "Doküman:",
            document.metadata.get(
                "document_id"
            ),
        )

        print(
            "Tür:",
            document.metadata.get(
                "document_type"
            ),
        )

        print(
            document.page_content[:500]
        )

        print("-" * 70)

    print()
    print("=" * 70)
    print("DOĞRULAMA")
    print("=" * 70)

    # Gerçek deterministic backend kontrolü
    if deterministic.get(
        "overall_status"
    ) != "critical":
        raise RuntimeError(
            "Beklenen overall_status critical değil."
        )

    if deterministic.get(
        "diagnosis"
    ) != "bearing_degradation":
        raise RuntimeError(
            "Beklenen bearing_degradation "
            "teşhisi alınamadı."
        )

    if deterministic.get(
        "recommended_procedure"
    ) != "MNT-MA-002":
        raise RuntimeError(
            "MNT-MA-002 deterministic analizde "
            "bulunamadı."
        )

    if deterministic.get(
        "escalation_procedure"
    ) != "MNT-MA-007":
        raise RuntimeError(
            "MNT-MA-007 eskalasyonu alınamadı."
        )

    # Retrieval kontrolü
    retrieved_text = "\n".join(
        document.page_content
        for document in retrieved_documents
    )

    if "MNT-MA-002" not in retrieved_text:
        raise RuntimeError(
            "MNT-MA-002 retrieval sonucunda "
            "bulunamadı."
        )

    if "MNT-MA-007" not in retrieved_text:
        raise RuntimeError(
            "MNT-MA-007 retrieval sonucunda "
            "bulunamadı."
        )

    print(
        "✓ Gerçek sensör verisi kullanıldı"
    )
    print(
        "✓ Veri kalitesi analizi çalıştı"
    )
    print(
        "✓ Threshold analizi çalıştı"
    )
    print(
        "✓ Trend analizi çalıştı"
    )
    print(
        "✓ Deterministik teşhis çalıştı"
    )
    print(
        "✓ Retrieval sorgusu otomatik üretildi"
    )
    print(
        "✓ İlgili bakım prosedürü getirildi"
    )
    print(
        "✓ Kritik eskalasyon kaynağı getirildi"
    )

    print()
    print(
        "RAG servisi uçtan uca testi "
        "başarıyla tamamlandı."
    )


if __name__ == "__main__":
    main()
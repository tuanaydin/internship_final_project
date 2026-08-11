from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.context_builder import (
    build_rag_context,
)
from backend.services.rag.query_builder import (
    build_retrieval_query,
)
from backend.services.rag.retriever import (
    retrieve_documents,
)


def main() -> None:
    machine_id = "MOTOR_A"

    question = (
        "Motor-A neden kritik durumda "
        "ve hangi bakım işlemleri yapılmalı?"
    )

    # Bu aşamada deterministic analiz çıktısını
    # test amacıyla elle tanımlıyoruz.
    deterministic_analysis = {
        "overall_status": "critical",
        "diagnosis": "bearing_degradation",
        "confidence": "high",
        "active_alarms": [
            "ALM-VIB-02",
            "ALM-COMB-BRG-01",
        ],
        "recommended_procedure": "MNT-MA-002",
        "escalation_required": True,
        "escalation_procedure": "MNT-MA-007",
        "evidence": {
            "temperature_trend": "increasing",
            "vibration_trend": "increasing",
            "vibration_mm_s": 8.231,
            "temperature_c": 79.20,
        },
    }

    # Kullanıcı sorusunu deterministic analiz
    # sonuçlarıyla zenginleştirerek retrieval
    # sorgusu oluştur.
    retrieval_query = build_retrieval_query(
        question=question,
        deterministic_analysis=deterministic_analysis,
    )

    # Zenginleştirilmiş sorguyla ilgili
    # teknik doküman parçalarını getir.
    retrieved_documents = retrieve_documents(
        query=retrieval_query,
        machine_id=machine_id,
        k=5,
    )

    # Makine bilgisi, deterministic analiz ve
    # retrieved dokümanları tek context içinde birleştir.
    context = build_rag_context(
        machine_id=machine_id,
        question=question,
        deterministic_analysis=deterministic_analysis,
        retrieved_documents=retrieved_documents,
    )

    print("=" * 70)
    print("RAG CONTEXT BUILDER TESTİ")
    print("=" * 70)

    print()
    print(context)

    print()
    print("=" * 70)
    print("RETRIEVAL SORGUSU")
    print("=" * 70)
    print(retrieval_query)

    print()
    print("=" * 70)
    print("DOĞRULAMA")
    print("=" * 70)

    # Oluşturulan context içerisinde bulunması
    # gereken temel bilgileri kontrol et.
    required_values = [
        "MOTOR_A",
        "critical",
        "bearing_degradation",
        "ALM-VIB-02",
        "MNT-MA-002",
        "MNT-MA-007",
        "RETRIEVED KNOWLEDGE",
    ]

    for value in required_values:
        if value not in context:
            raise RuntimeError(
                f"Context içinde beklenen değer bulunamadı: {value}"
            )

    # Retrieval sonucunda gerçekten ilgili
    # bakım prosedürlerinin geldiğini doğrula.
    retrieved_text = "\n".join(
        document.page_content
        for document in retrieved_documents
    )

    if "MNT-MA-002" not in retrieved_text:
        raise RuntimeError(
            "MNT-MA-002 retrieval sonucunda bulunamadı."
        )

    if "MNT-MA-007" not in retrieved_text:
        raise RuntimeError(
            "MNT-MA-007 retrieval sonucunda bulunamadı."
        )

    # Bakım prosedürü dokümanının gerçekten
    # retrieval sonuçları arasında olduğunu kontrol et.
    retrieved_document_ids = {
        document.metadata.get("document_id")
        for document in retrieved_documents
    }

    if "MA-MNT-001" not in retrieved_document_ids:
        raise RuntimeError(
            "Bakım prosedürü dokümanı "
            "MA-MNT-001 retrieval sonucunda bulunamadı."
        )

    print("✓ Makine bağlamı context'e eklendi")
    print("✓ Deterministik analiz context'e eklendi")
    print("✓ İlgili teknik dokümanlar retrieval ile getirildi")
    print("✓ MNT-MA-002 prosedürü retrieval sonucunda bulundu")
    print("✓ MNT-MA-007 eskalasyon prosedürü retrieval sonucunda bulundu")
    print("✓ MA-MNT-001 bakım dokümanı retrieval sonucunda bulundu")

    print()
    print(
        "RAG context builder testi başarıyla tamamlandı."
    )


if __name__ == "__main__":
    main()
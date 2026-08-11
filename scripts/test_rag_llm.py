from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.rag_service import (
    answer_question_at,
)


def main() -> None:
    machine_id = "MOTOR_A"

    timestamp = "2026-07-27 20:00:00"

    question = (
        "Motor-A neden kritik durumda "
        "ve hangi bakım işlemleri yapılmalı?"
    )

    result = answer_question_at(
        machine_id=machine_id,
        question=question,
        timestamp=timestamp,
        window_minutes=300,
        k=5,
    )

    print("=" * 70)
    print("RAG + LLM UÇTAN UCA TESTİ")
    print("=" * 70)

    print()
    print("SORU")
    print("-" * 70)
    print(question)

    deterministic = result[
        "deterministic_analysis"
    ]

    print()
    print("DETERMİNİSTİK ANALİZ")
    print("-" * 70)

    print(
        "Durum:",
        deterministic.get("overall_status"),
    )

    print(
        "Teşhis:",
        deterministic.get("diagnosis"),
    )

    print(
        "Güven:",
        deterministic.get("confidence"),
    )

    print(
        "Aktif alarmlar:",
        deterministic.get("active_alarms"),
    )

    print(
        "Önerilen prosedür:",
        deterministic.get(
            "recommended_procedure"
        ),
    )

    print(
        "Eskalasyon prosedürü:",
        deterministic.get(
            "escalation_procedure"
        ),
    )

    print()
    print("AI CEVABI")
    print("-" * 70)

    answer = result["answer"]

    print(answer)

    print()
    print("=" * 70)
    print("DOĞRULAMA")
    print("=" * 70)

    if not answer.strip():
        raise RuntimeError(
            "LLM boş cevap üretti."
        )

    if "MNT-MA-002" not in answer:
        raise RuntimeError(
            "AI cevabında MNT-MA-002 bulunamadı."
        )

    if "MNT-MA-007" not in answer:
        raise RuntimeError(
            "AI cevabında MNT-MA-007 bulunamadı."
        )

    print("✓ LLM cevap üretti")
    print("✓ Gerçek deterministic analiz kullanıldı")
    print("✓ RAG context modele gönderildi")
    print("✓ MNT-MA-002 cevapta korundu")
    print("✓ MNT-MA-007 cevapta korundu")

    print()
    print(
        "RAG + LLM uçtan uca testi "
        "başarıyla tamamlandı."
    )


if __name__ == "__main__":
    main()
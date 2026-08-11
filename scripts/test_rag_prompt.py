from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.prompt import (
    create_rag_prompt,
)
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

    rag_result = prepare_rag_context_at(
        machine_id=machine_id,
        question=question,
        timestamp=timestamp,
        window_minutes=300,
        k=5,
    )

    prompt = create_rag_prompt()

    messages = prompt.format_messages(
        question=question,
        context=rag_result["context"],
    )

    print("=" * 70)
    print("RAG PROMPT TESTİ")
    print("=" * 70)

    for index, message in enumerate(
        messages,
        start=1,
    ):
        print()
        print(
            f"[{index}] Mesaj türü: "
            f"{message.type}"
        )

        print("-" * 70)

        print(message.content)

        print("-" * 70)

    print()
    print("=" * 70)
    print("DOĞRULAMA")
    print("=" * 70)

    combined_content = "\n".join(
        str(message.content)
        for message in messages
    )

    required_values = [
        "bearing_degradation",
        "ALM-VIB-02",
        "MNT-MA-002",
        "MNT-MA-007",
        "MA-MNT-001",
    ]

    for value in required_values:
        if value not in combined_content:
            raise RuntimeError(
                "Prompt içerisinde beklenen "
                f"değer bulunamadı: {value}"
            )

    print("✓ System prompt oluşturuldu")
    print("✓ Kullanıcı sorusu prompt'a eklendi")
    print("✓ Deterministik analiz prompt'a eklendi")
    print("✓ Retrieved kaynaklar prompt'a eklendi")
    print("✓ Kritik prosedür bilgileri korunuyor")

    print()
    print(
        "RAG prompt testi başarıyla tamamlandı."
    )


if __name__ == "__main__":
    main()
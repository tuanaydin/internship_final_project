from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.services.rag.llm_service import (
    create_chat_model,
)


def main() -> None:
    print("=" * 70)
    print("LLM BAĞLANTI TESTİ")
    print("=" * 70)

    model = create_chat_model()

    response = model.invoke(
        "Sadece 'LLM bağlantısı başarılı.' yaz."
    )

    print()
    print("MODEL CEVABI")
    print("-" * 70)
    print(response.text)

    if not response.content:
        raise RuntimeError(
            "LLM boş cevap üretti."
        )

    print()
    print("✓ Gemini modeli oluşturuldu")
    print("✓ API bağlantısı kuruldu")
    print("✓ Model cevap üretti")

    print()
    print(
        "LLM bağlantı testi başarıyla tamamlandı."
    )


if __name__ == "__main__":
    main()
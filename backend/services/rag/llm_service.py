from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from backend.core.config import PROJECT_ROOT


load_dotenv(PROJECT_ROOT / ".env")


DEFAULT_MODEL = "google_genai:gemini-3.5-flash-lite"


@lru_cache(maxsize=1)
def create_chat_model() -> BaseChatModel:
    """
    RAG cevap üretiminde kullanılacak
    chat modelini oluşturur.
    """

    model_name = os.getenv(
        "RAG_MODEL",
        DEFAULT_MODEL,
    )

    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError(
            "GOOGLE_API_KEY .env dosyasında bulunamadı."
        )

    return init_chat_model(
        model_name,
        #temperature=0.1,
        max_retries=3,
    )
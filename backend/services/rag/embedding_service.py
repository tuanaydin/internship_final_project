from __future__ import annotations
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

@lru_cache(maxsize=1)
def create_embedding_model() -> HuggingFaceEmbeddings:
    """
    Türkçe dahil çok dilli semantic search için
    local Hugging Face embedding modeli oluşturur.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )
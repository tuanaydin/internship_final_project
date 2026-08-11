from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssistantAskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Makine hakkında sorulacak bakım sorusu.",
    )

    timestamp: str = Field(
        description=(
            "Analizin yapılacağı zaman. "
            "Örnek: 2026-07-27 20:00:00"
        ),
    )

    window_minutes: int = Field(
        default=60,
        ge=5,
        le=1440,
        description="Trend analizi için geçmiş zaman penceresi.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="RAG retrieval sonucunda getirilecek chunk sayısı.",
    )


class AssistantSourceSchema(BaseModel):
    document_id: str | None = None
    document_type: str | None = None
    chunk_id: str | None = None
    source: str | None = None
    page_number: int | None = None


class AssistantAskResponse(BaseModel):
    machine_id: str
    timestamp: str
    question: str
    window_minutes: int

    deterministic_analysis: dict[str, Any]

    answer: str

    sources: list[AssistantSourceSchema] = Field(
        default_factory=list
    )
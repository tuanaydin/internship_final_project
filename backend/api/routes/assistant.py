from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.assistant import (
    AssistantAskRequest,
    AssistantAskResponse,
)
from backend.services.asset_service import (
    get_machine,
)
from backend.services.rag.rag_service import (
    answer_question_at,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Assistant"],
)


@router.post(
    "/machines/{machine_id}/assistant/ask",
    response_model=AssistantAskResponse,
)
def ask_machine_assistant(
    machine_id: str,
    request: AssistantAskRequest,
):
    """
    Belirtilen makine ve timestamp için
    deterministic IoT analizi + RAG + LLM
    kullanarak bakım sorusunu cevaplar.
    """

    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    try:
        result = answer_question_at(
            machine_id=machine_id,
            question=request.question,
            timestamp=request.timestamp,
            window_minutes=request.window_minutes,
            k=request.top_k,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    sources = []

    seen_chunks: set[str] = set()

    for document in result["retrieved_documents"]:
        metadata = document.metadata

        chunk_id = metadata.get("chunk_id")

        if (
            chunk_id
            and chunk_id in seen_chunks
        ):
            continue

        if chunk_id:
            seen_chunks.add(chunk_id)

        sources.append(
            {
                "document_id": metadata.get(
                    "document_id"
                ),
                "document_type": metadata.get(
                    "document_type"
                ),
                "chunk_id": chunk_id,
                "source": metadata.get(
                    "source"
                ),
                "page_number": metadata.get(
                    "page_number"
                ),
            }
        )

    return {
        "machine_id": machine_id,
        "timestamp": result[
            "requested_timestamp"
        ],
        "question": request.question,
        "window_minutes": request.window_minutes,
        "deterministic_analysis": result[
            "deterministic_analysis"
        ],
        "answer": result["answer"],
        "sources": sources,
    }
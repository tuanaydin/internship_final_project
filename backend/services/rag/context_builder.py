from __future__ import annotations

import json
from typing import Any

from langchain_core.documents import Document

from backend.services.asset_service import get_machine


def _format_deterministic_analysis(
    deterministic_analysis: dict[str, Any],
) -> str:
    """
    Deterministik analiz çıktısını LLM'e verilecek
    okunabilir JSON formatına dönüştürür.
    """

    return json.dumps(
        deterministic_analysis,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def _format_retrieved_documents(
    documents: list[Document],
) -> str:
    """
    Retriever tarafından dönen chunk'ları
    kaynak bilgileriyle birlikte metne dönüştürür.
    """

    if not documents:
        return "İlgili teknik kaynak bulunamadı."

    sections: list[str] = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        source_lines = [
            f"SOURCE {index}",
            f"Document ID: {metadata.get('document_id')}",
            f"Document Type: {metadata.get('document_type')}",
            f"Chunk ID: {metadata.get('chunk_id')}",
            f"Source File: {metadata.get('source')}",
        ]

        page_number = metadata.get(
            "page_number"
        )

        if page_number is not None:
            source_lines.append(
                f"Page: {page_number}"
            )

        source_lines.append(
            "Content:"
        )

        source_lines.append(
            document.page_content.strip()
        )

        sections.append(
            "\n".join(source_lines)
        )

    return "\n\n---\n\n".join(
        sections
    )


def build_rag_context(
    machine_id: str,
    question: str,
    deterministic_analysis: dict[str, Any],
    retrieved_documents: list[Document],
) -> str:
    """
    Makine bağlamını, deterministik analiz sonucunu
    ve RAG ile getirilen teknik kaynakları tek bir
    context içerisinde birleştirir.
    """

    machine = get_machine(machine_id)

    if machine is None:
        raise ValueError(
            f"Machine not found: {machine_id}"
        )

    if not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    deterministic_text = (
        _format_deterministic_analysis(
            deterministic_analysis
        )
    )

    retrieved_text = (
        _format_retrieved_documents(
            retrieved_documents
        )
    )

    context = f"""
=== USER QUESTION ===
{question}

=== MACHINE CONTEXT ===
Plant ID: {machine.get("plant_id")}
Station ID: {machine.get("station_id")}
Machine ID: {machine_id}
Machine Name: {machine.get("name")}
Machine Type: {machine.get("type")}

=== DETERMINISTIC ANALYSIS ===
{deterministic_text}

=== RETRIEVED KNOWLEDGE ===
{retrieved_text}
""".strip()

    return context
from __future__ import annotations

from typing import Any


def build_retrieval_query(
    question: str,
    deterministic_analysis: dict[str, Any],
) -> str:
    """
    Kullanıcı sorusunu deterministic analiz
    kanıtlarıyla zenginleştirerek retrieval
    sorgusu oluşturur.
    """

    parts: list[str] = [
        question.strip()
    ]

    overall_status = deterministic_analysis.get(
        "overall_status"
    )

    diagnosis = deterministic_analysis.get(
        "diagnosis"
    )

    confidence = deterministic_analysis.get(
        "confidence"
    )

    active_alarms = deterministic_analysis.get(
        "active_alarms",
        [],
    )

    recommended_procedure = (
        deterministic_analysis.get(
            "recommended_procedure"
        )
    )

    escalation_procedure = (
        deterministic_analysis.get(
            "escalation_procedure"
        )
    )

    evidence = deterministic_analysis.get(
        "evidence",
        {},
    )

    if overall_status:
        parts.append(
            f"Overall status: {overall_status}"
        )

    if diagnosis:
        parts.append(
            f"Diagnosis: {diagnosis}"
        )

    if confidence:
        parts.append(
            f"Confidence: {confidence}"
        )

    if active_alarms:
        parts.append(
            "Active alarms: "
            + ", ".join(active_alarms)
        )

    if recommended_procedure:
        parts.append(
            "Recommended procedure: "
            f"{recommended_procedure}"
        )

    if escalation_procedure:
        parts.append(
            "Escalation procedure: "
            f"{escalation_procedure}"
        )

    if evidence:
        evidence_text = ", ".join(
            f"{key}: {value}"
            for key, value in evidence.items()
        )

        parts.append(
            f"Evidence: {evidence_text}"
        )

    return "\n".join(parts)
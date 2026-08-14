from __future__ import annotations

from typing import Any

from backend.services.anomaly_service import (
    analyze_measurement,
)
from backend.services.data_quality_service import (
    analyze_data_quality,
)
#from backend.services.data_service import (get_measurements_until,)
from backend.services.data_service import (
    get_measurements_in_window,
)


from backend.services.diagnostic_service import (
    diagnose_machine,
)
from backend.services.trend_service import (
    analyze_trends,
)

from backend.services.rag.context_builder import (
    build_rag_context,
)
from backend.services.rag.query_builder import (
    build_retrieval_query,
)
from backend.services.rag.retriever import (
    retrieve_documents,
)
from backend.services.rag.rag_chain import (
    create_rag_chain,
)

from backend.services.asset_service import (
    get_machine_by_id,
)


def _get_trend_direction(
    trend_analysis: dict[str, Any],
    sensor_name: str,
) -> str | None:
    """
    Trend analizinden ilgili sensörün
    yön bilgisini getirir.
    """

    for trend in trend_analysis.get(
        "trends",
        [],
    ):
        if trend.get("sensor") == sensor_name:
            return trend.get("direction")

    return None


def _build_deterministic_summary(
    measurement: dict[str, Any],
    data_quality: dict[str, Any],
    threshold_analysis: dict[str, Any],
    trend_analysis: dict[str, Any],
    diagnosis: dict[str, Any],
) -> dict[str, Any]:
    """
    Backend servislerinden gelen detaylı çıktıları,
    RAG retrieval ve LLM context'i için daha küçük
    ve anlamlı bir özet haline getirir.
    """

    active_alarms = list(
        threshold_analysis.get(
            "active_alarms",
            [],
        )
    )

    diagnosis_alarm = diagnosis.get(
        "alarm_code"
    )

    if (
        diagnosis_alarm
        and diagnosis_alarm not in active_alarms
    ):
        active_alarms.append(
            diagnosis_alarm
        )

    evidence = {
        "temperature_c": measurement.get(
            "temperature_c"
        ),
        "vibration_mm_s": measurement.get(
            "vibration_mm_s"
        ),
        "current_a": measurement.get(
            "current_a"
        ),
        "load_pct": measurement.get(
            "load_pct"
        ),
        "power_kw": measurement.get(
            "power_kw"
        ),
        "temperature_trend": (
            _get_trend_direction(
                trend_analysis,
                "temperature_c",
            )
        ),
        "vibration_trend": (
            _get_trend_direction(
                trend_analysis,
                "vibration_mm_s",
            )
        ),
        "current_trend": (
            _get_trend_direction(
                trend_analysis,
                "current_a",
            )
        ),
        "load_trend": (
            _get_trend_direction(
                trend_analysis,
                "load_pct",
            )
        ),
        "power_trend": (
            _get_trend_direction(
                trend_analysis,
                "power_kw",
            )
        ),
    }

    # None değerleri retrieval sorgusunu
    # gereksiz yere kirletmesin.
    evidence = {
        key: value
        for key, value in evidence.items()
        if value is not None
    }

    return {
        "timestamp": measurement.get(
            "timestamp"
        ),
        "data_quality_status": (
            data_quality.get("status")
        ),
        "overall_status": (
            threshold_analysis.get(
                "overall_status"
            )
        ),
        "diagnosis": diagnosis.get(
            "diagnosis"
        ),
        "confidence": diagnosis.get(
            "confidence"
        ),
        "active_alarms": active_alarms,
        "recommended_procedure": (
            diagnosis.get(
                "recommended_procedure"
            )
        ),
        "escalation_required": (
            diagnosis.get(
                "escalation_required",
                False,
            )
        ),
        "escalation_procedure": (
            diagnosis.get(
                "escalation_procedure"
            )
        ),
        "evidence": evidence,
    }


def prepare_rag_context_at(
    machine_id: str,
    question: str,
    timestamp: str,
    window_minutes: int = 60,
    k: int = 5,
) -> dict[str, Any]:
    """
    Belirli bir timestamp için gerçek IoT analizini
    çalıştırır, retrieval yapar ve LLM'e hazır
    RAG context'i oluşturur.
    """

    if not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if window_minutes <= 0:
        raise ValueError(
            "window_minutes must be greater than zero."
        )

    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )
    machine = get_machine_by_id(machine_id)

    if machine is None:
        raise ValueError(
            f"Machine '{machine_id}' not found."
        )
    """
    # Motor-A dummy dataset şu anda
    # 5 dakikalık örnekleme kullanıyor.
    measurement_limit = (
        window_minutes // 5
    ) + 1

    measurements = get_measurements_until(
        machine_id=machine_id,
        timestamp=timestamp,
        limit=measurement_limit,
    )   
    """
    measurements = get_measurements_in_window(
        machine_id=machine_id,
        timestamp=timestamp,
        window_minutes=window_minutes,
        )

    if not measurements:
        raise ValueError(
            "No measurements found for the "
            "requested timestamp."
        )

    latest_measurement = measurements[-1]

    # 1. Veri kalitesi
    data_quality = analyze_data_quality(
        machine_id,
        measurements,
    )

    # 2. Threshold / alarm
    threshold_analysis = analyze_measurement(
        machine_id,
        latest_measurement,
    )

    # 3. Trend
    trend_analysis = analyze_trends(
        measurements
    )

    # 4. Deterministik teşhis
    diagnosis = diagnose_machine(
        measurement=latest_measurement,
        trend_analysis=trend_analysis,
        data_quality=data_quality,
        threshold_analysis=threshold_analysis,
        asset_type=machine["type"],
    )

    # 5. RAG için kompakt deterministic özet
    deterministic_analysis = (
        _build_deterministic_summary(
            measurement=latest_measurement,
            data_quality=data_quality,
            threshold_analysis=threshold_analysis,
            trend_analysis=trend_analysis,
            diagnosis=diagnosis,
        )
    )

    # 6. Deterministic-aware retrieval sorgusu
    retrieval_query = build_retrieval_query(
        question=question,
        deterministic_analysis=(
            deterministic_analysis
        ),
    )

    # 7. Semantic retrieval
    retrieved_documents = retrieve_documents(
        query=retrieval_query,
        machine_id=machine_id,
        k=k,
    )

    # 8. LLM'e verilecek context
    context = build_rag_context(
        machine_id=machine_id,
        question=question,
        deterministic_analysis=(
            deterministic_analysis
        ),
        retrieved_documents=(
            retrieved_documents
        ),
    )

    return {
        "machine_id": machine_id,
        "requested_timestamp": timestamp,
        "window_minutes": window_minutes,
        "question": question,

        "measurement": latest_measurement,

        "data_quality": data_quality,
        "threshold_analysis": threshold_analysis,
        "trend_analysis": trend_analysis,
        "diagnosis": diagnosis,

        "deterministic_analysis": (
            deterministic_analysis
        ),

        "retrieval_query": retrieval_query,

        "retrieved_documents": (
            retrieved_documents
        ),

        "context": context,
    }

def answer_question_at(
    machine_id: str,
    question: str,
    timestamp: str,
    window_minutes: int = 60,
    k: int = 5,
) -> dict[str, Any]:
    """
    Deterministik analiz, retrieval ve LLM kullanarak
    kullanıcı sorusuna kanıta dayalı RAG cevabı üretir.
    """

    rag_result = prepare_rag_context_at(
        machine_id=machine_id,
        question=question,
        timestamp=timestamp,
        window_minutes=window_minutes,
        k=k,
    )

    chain = create_rag_chain()

    answer = chain.invoke(
        {
            "question": question,
            "context": rag_result["context"],
        }
    )

    return {
        **rag_result,
        "answer": answer,
    }
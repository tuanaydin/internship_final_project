from backend.services.rag import rag_service


def test_rag_context_uses_time_based_measurement_window(
    monkeypatch,
):
    """
    RAG deterministic context'i kayıt sayısı veya
    sabit sampling varsayımı yerine gerçek zaman
    penceresini kullanmalıdır.
    """

    captured = {}

    measurements = [
        {
            "timestamp": "2026-07-27 19:53:00",
            "device_id": "MOTOR_A",
            "operating_state": "running",
            "load_pct": 70.0,
            "temperature_c": 70.0,
            "vibration_mm_s": 2.5,
            "current_a": 18.0,
            "power_kw": 10.0,
        },
        {
            "timestamp": "2026-07-27 20:00:00",
            "device_id": "MOTOR_A",
            "operating_state": "running",
            "load_pct": 72.0,
            "temperature_c": 71.0,
            "vibration_mm_s": 2.6,
            "current_a": 18.5,
            "power_kw": 10.2,
        },
    ]

    def fake_get_measurements_in_window(
        machine_id,
        timestamp,
        window_minutes,
    ):
        captured["machine_id"] = machine_id
        captured["timestamp"] = timestamp
        captured["window_minutes"] = window_minutes

        return measurements

    monkeypatch.setattr(
        rag_service,
        "get_measurements_in_window",
        fake_get_measurements_in_window,
    )

    monkeypatch.setattr(
        rag_service,
        "get_machine_by_id",
        lambda machine_id: {
            "id": machine_id,
            "type": "electric_motor",
        },
    )

    monkeypatch.setattr(
        rag_service,
        "analyze_data_quality",
        lambda machine_id, values: {
            "status": "ok",
            "issues": [],
        },
    )

    monkeypatch.setattr(
        rag_service,
        "analyze_measurement",
        lambda machine_id, measurement: {
            "overall_status": "normal",
            "active_alarms": [],
            "sensor_analysis": [],
        },
    )

    monkeypatch.setattr(
        rag_service,
        "analyze_trends",
        lambda values: {
            "trends": [],
        },
    )

    monkeypatch.setattr(
        rag_service,
        "diagnose_machine",
        lambda **kwargs: {
            "status": "no_pattern",
            "diagnosis": None,
            "confidence": "low",
            "alarm_code": None,
            "recommended_procedure": None,
            "escalation_required": False,
            "escalation_procedure": None,
            "evidence": [],
            "message": "No deterministic pattern matched.",
        },
    )

    monkeypatch.setattr(
        rag_service,
        "build_retrieval_query",
        lambda **kwargs: "test retrieval query",
    )

    monkeypatch.setattr(
        rag_service,
        "retrieve_documents",
        lambda **kwargs: [],
    )

    monkeypatch.setattr(
        rag_service,
        "build_rag_context",
        lambda **kwargs: "test context",
    )

    result = rag_service.prepare_rag_context_at(
        machine_id="MOTOR_A",
        question="What is happening?",
        timestamp="2026-07-27 20:00:00",
        window_minutes=7,
        k=5,
    )

    assert captured == {
        "machine_id": "MOTOR_A",
        "timestamp": "2026-07-27 20:00:00",
        "window_minutes": 7,
    }

    assert (
        result["measurement"]["timestamp"]
        == "2026-07-27 20:00:00"
    )

    assert result["window_minutes"] == 7
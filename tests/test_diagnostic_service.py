from backend.services.diagnostic_service import diagnose_machine


def test_overload_diagnosis_includes_critical_escalation():
    measurement = {
        "temperature_c": 75.64,
        "vibration_mm_s": 3.2,
        "current_a": 23.37,
        "load_pct": 95.74,
    }
    trend_analysis = {
        "trends": [
            {"sensor": "temperature_c", "direction": "stable"},
            {"sensor": "vibration_mm_s", "direction": "stable"},
            {"sensor": "current_a", "direction": "decreasing"},
            {"sensor": "load_pct", "direction": "stable"},
            {"sensor": "power_kw", "direction": "stable"},
        ]
    }
    data_quality = {"status": "ok"}
    threshold_analysis = {
        "overall_status": "critical",
        "sensor_analysis": [
            {"sensor": "temperature_c", "status": "warning"},
            {"sensor": "vibration_mm_s", "status": "normal"},
            {"sensor": "current_a", "status": "critical"},
            {"sensor": "load_pct", "status": "warning"},
        ],
    }

    result = diagnose_machine(
        measurement,
        trend_analysis,
        data_quality,
        threshold_analysis,
    )

    assert result["status"] == "diagnosed"
    assert result["diagnosis"] == "overload"
    assert result["escalation_required"] is True
    assert result["escalation_procedure"] == "MNT-MA-007"

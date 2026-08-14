from backend.services.diagnostic_service import (
    diagnose_machine,
)


def test_overload_diagnosis_includes_critical_escalation():
    measurement = {
        "temperature_c": 75.64,
        "vibration_mm_s": 3.2,
        "current_a": 23.37,
        "load_pct": 95.74,
    }

    trend_analysis = {
        "trends": [
            {
                "sensor": "temperature_c",
                "direction": "stable",
            },
            {
                "sensor": "vibration_mm_s",
                "direction": "stable",
            },
            {
                "sensor": "current_a",
                "direction": "decreasing",
            },
            {
                "sensor": "load_pct",
                "direction": "stable",
            },
            {
                "sensor": "power_kw",
                "direction": "stable",
            },
        ]
    }

    data_quality = {
        "status": "ok",
    }

    threshold_analysis = {
        "overall_status": "critical",
        "sensor_analysis": [
            {
                "sensor": "temperature_c",
                "status": "warning",
            },
            {
                "sensor": "vibration_mm_s",
                "status": "normal",
            },
            {
                "sensor": "current_a",
                "status": "critical",
            },
            {
                "sensor": "load_pct",
                "status": "warning",
            },
        ],
    }

    result = diagnose_machine(
        measurement=measurement,
        trend_analysis=trend_analysis,
        data_quality=data_quality,
        threshold_analysis=threshold_analysis,
        asset_type="electric_motor",
    )

    assert result["status"] == "diagnosed"
    assert result["diagnosis"] == "overload"
    assert result["recommended_procedure"] == "MNT-MA-003"
    assert result["escalation_required"] is True
    assert result["escalation_procedure"] == "MNT-MA-007"


def test_critical_pump_does_not_use_motor_diagnosis_or_procedure():
    """
    Pump verisi Motor-A bearing pattern'ına benzese bile
    electric_motor diagnosis kuralları çalışmamalıdır.
    """

    measurement = {
        "temperature_c": 82.0,
        "vibration_mm_s": 5.2,
        "current_a": 20.5,
        "load_pct": 94.0,
    }

    trend_analysis = {
        "trends": [
            {
                "sensor": "temperature_c",
                "direction": "increasing",
            },
            {
                "sensor": "vibration_mm_s",
                "direction": "increasing",
            },
            {
                "sensor": "current_a",
                "direction": "stable",
            },
            {
                "sensor": "load_pct",
                "direction": "stable",
            },
        ]
    }

    data_quality = {
        "status": "ok",
    }

    threshold_analysis = {
        "overall_status": "critical",
        "sensor_analysis": [
            {
                "sensor": "temperature_c",
                "status": "critical",
            },
            {
                "sensor": "vibration_mm_s",
                "status": "critical",
            },
            {
                "sensor": "current_a",
                "status": "warning",
            },
            {
                "sensor": "load_pct",
                "status": "warning",
            },
        ],
    }

    result = diagnose_machine(
        measurement=measurement,
        trend_analysis=trend_analysis,
        data_quality=data_quality,
        threshold_analysis=threshold_analysis,
        asset_type="centrifugal_pump",
    )

    assert result["status"] == "no_pattern"
    assert result["diagnosis"] is None
    assert result["alarm_code"] is None

    assert result["recommended_procedure"] is None
    assert result["escalation_required"] is False
    assert result["escalation_procedure"] is None


def test_critical_valve_does_not_use_motor_escalation_procedure():
    """
    Critical bir control valve için generic critical fallback
    Motor-A'nın MNT-MA-007 prosedürünü üretmemelidir.
    """

    measurement = {
        "temperature_c": 80.0,
        "current_a": 4.2,
    }

    trend_analysis = {
        "trends": [
            {
                "sensor": "temperature_c",
                "direction": "stable",
            },
            {
                "sensor": "current_a",
                "direction": "stable",
            },
        ]
    }

    data_quality = {
        "status": "ok",
    }

    threshold_analysis = {
        "overall_status": "critical",
        "sensor_analysis": [
            {
                "sensor": "temperature_c",
                "status": "critical",
            },
        ],
    }

    result = diagnose_machine(
        measurement=measurement,
        trend_analysis=trend_analysis,
        data_quality=data_quality,
        threshold_analysis=threshold_analysis,
        asset_type="control_valve",
    )

    assert result["status"] == "no_pattern"
    assert result["diagnosis"] is None
    assert result["recommended_procedure"] is None

    assert result["escalation_required"] is False
    assert result["escalation_procedure"] is None

    assert result["escalation_procedure"] != "MNT-MA-007"
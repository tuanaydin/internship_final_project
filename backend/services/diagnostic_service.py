from __future__ import annotations

from typing import Any


def _get_trend(
    trend_analysis: dict[str, Any],
    sensor_name: str,
) -> dict[str, Any] | None:
    """
    Belirtilen sensörün trend sonucunu bulur.
    """

    for trend in trend_analysis.get("trends", []):
        if trend.get("sensor") == sensor_name:
            return trend

    return None


def _get_sensor_analysis(
    threshold_analysis: dict[str, Any],
    sensor_name: str,
) -> dict[str, Any] | None:
    """
    Threshold analizinden belirtilen sensör sonucunu bulur.
    """

    for sensor in threshold_analysis.get("sensor_analysis", []):
        if sensor.get("sensor") == sensor_name:
            return sensor

    return None


def _requires_critical_escalation(
    threshold_analysis: dict[str, Any],
) -> bool:
    """
    Threshold analizinde herhangi bir kritik durum
    olup olmadığını kontrol eder.
    """

    return (
        threshold_analysis.get("overall_status")
        == "critical"
    )


def diagnose_machine(
    measurement: dict[str, Any],
    trend_analysis: dict[str, Any],
    data_quality: dict[str, Any],
    threshold_analysis: dict[str, Any],
    asset_type: str,
) -> dict[str, Any]:
    """
    Veri kalitesi, threshold sonuçları ve trendleri kullanarak
    deterministik çoklu sensör teşhis desenlerini değerlendirir.
    """

    # --------------------------------------------------
    # 1. VERİ KALİTESİ
    # --------------------------------------------------

    if data_quality.get("status") != "ok":
        return {
            "status": "conditional",
            "diagnosis": None,
            "confidence": "low",
            "alarm_code": None,
            "recommended_procedure": None,
            "escalation_required": False,
            "escalation_procedure": None,
            "evidence": [],
            "message": (
                "Sensor data is not reliable enough for a physical "
                "fault diagnosis. Resolve data-quality issues first."
            ),
        }

    # --------------------------------------------------
    # 2. ASSET TYPE / DIAGNOSTIC PROFILE
    # --------------------------------------------------
    #
    # Bu MVP'de fiziksel deterministik teşhis kuralları
    # yalnızca electric_motor tipi için tanımlıdır.
    #
    # Desteklenmeyen asset tiplerinde Motor-A'ya ait
    # alarm veya bakım prosedürleri üretilmemelidir.
    # --------------------------------------------------

    if asset_type != "electric_motor":
        return {
            "status": "no_pattern",
            "diagnosis": None,
            "confidence": "low",
            "alarm_code": None,
            "recommended_procedure": None,
            "escalation_required": False,
            "escalation_procedure": None,
            "evidence": [
                f"asset_type={asset_type}",
            ],
            "message": (
                "No deterministic physical diagnosis rules are "
                f"configured for asset type '{asset_type}'."
            ),
        }







    # --------------------------------------------------
    # 3. TREND SONUÇLARI
    # --------------------------------------------------

    temperature_trend = _get_trend(
        trend_analysis,
        "temperature_c",
    )

    vibration_trend = _get_trend(
        trend_analysis,
        "vibration_mm_s",
    )

    current_trend = _get_trend(
        trend_analysis,
        "current_a",
    )

    load_trend = _get_trend(
        trend_analysis,
        "load_pct",
    )

    power_trend = _get_trend(
        trend_analysis,
        "power_kw",
    )

    # --------------------------------------------------
    # 4. MEVCUT ÖLÇÜMLER
    # --------------------------------------------------

    vibration = measurement.get("vibration_mm_s")
    current = measurement.get("current_a")
    load = measurement.get("load_pct")

    # --------------------------------------------------
    # 5. THRESHOLD SONUÇLARI
    # --------------------------------------------------

    current_threshold = _get_sensor_analysis(
        threshold_analysis,
        "current_a",
    )

    load_threshold = _get_sensor_analysis(
        threshold_analysis,
        "load_pct",
    )

    critical_escalation = _requires_critical_escalation(
        threshold_analysis
    )

    # --------------------------------------------------
    # 6. BEARING DEGRADATION
    #
    # Sıcaklık ve titreşim birlikte yükseliyor.
    # --------------------------------------------------

    if (
        temperature_trend
        and vibration_trend
        and temperature_trend.get("direction") == "increasing"
        and vibration_trend.get("direction") == "increasing"
        and vibration is not None
        and vibration >= 3.5
    ):
        return {
            "status": "diagnosed",
            "diagnosis": "bearing_degradation",
            "confidence": "high",
            "alarm_code": "ALM-COMB-BRG-01",
            "recommended_procedure": "MNT-MA-002",
            "escalation_required": critical_escalation,
            "escalation_procedure": (
                "MNT-MA-007"
                if critical_escalation
                else None
            ),
            "evidence": [
                "temperature_trend=increasing",
                "vibration_trend=increasing",
                f"vibration_mm_s={vibration}",
            ],
            "message": (
                "Temperature and vibration are increasing together. "
                "The pattern supports a bearing, lubrication, or "
                "alignment issue."
            ),
        }

    # --------------------------------------------------
    # 7. OVERLOAD
    #
    # Yük ve akım eşik üzerinde ise overload deseni
    # desteklenir. Trendler ek kanıt olarak kullanılır.
    # --------------------------------------------------

    load_status = (
        load_threshold.get("status")
        if load_threshold
        else None
    )

    current_status = (
        current_threshold.get("status")
        if current_threshold
        else None
    )

    if (
        load is not None
        and current is not None
        and load > 92
        and current >= 19
        and load_status in {"warning", "critical"}
        and current_status in {"warning", "critical"}
    ):
        evidence = [
            f"load_pct={load}",
            f"load_status={load_status}",
            f"current_a={current}",
            f"current_status={current_status}",
        ]

        if load_trend:
            evidence.append(
                f"load_trend={load_trend.get('direction')}"
            )

        if current_trend:
            evidence.append(
                f"current_trend={current_trend.get('direction')}"
            )

        if power_trend:
            evidence.append(
                f"power_trend={power_trend.get('direction')}"
            )

        return {
            "status": "diagnosed",
            "diagnosis": "overload",
            "confidence": "high",
            "alarm_code": "ALM-COMB-OVL-01",
            "recommended_procedure": "MNT-MA-003",
            "escalation_required": critical_escalation,
            "escalation_procedure": (
                "MNT-MA-007"
                if critical_escalation
                else None
            ),
            "evidence": evidence,
            "message": (
                "Load and current are above the documented "
                "operating thresholds. The multi-sensor pattern "
                "supports an overload condition."
            ),
        }

    # --------------------------------------------------
    # 8. COOLING DEGRADATION
    #
    # Sıcaklık yükselirken titreşim normal kalıyor.
    # --------------------------------------------------

    if (
        temperature_trend
        and vibration_trend
        and temperature_trend.get("direction") == "increasing"
        and vibration_trend.get("direction") in {
            "stable",
            "decreasing",
        }
        and vibration is not None
        and vibration < 3.5
    ):
        return {
            "status": "diagnosed",
            "diagnosis": "cooling_degradation",
            "confidence": "medium",
            "alarm_code": "ALM-COMB-COOL-01",
            "recommended_procedure": "MNT-MA-001",
            "escalation_required": critical_escalation,
            "escalation_procedure": (
                "MNT-MA-007"
                if critical_escalation
                else None
            ),
            "evidence": [
                "temperature_trend=increasing",
                (
                    "vibration_trend="
                    f"{vibration_trend.get('direction')}"
                ),
                f"vibration_mm_s={vibration}",
            ],
            "message": (
                "Temperature is increasing while vibration remains "
                "within the normal range. The pattern supports a "
                "possible cooling-performance issue."
            ),
        }

    # --------------------------------------------------
    # 9. TANIMLI DESEN BULUNAMADI
    # --------------------------------------------------

    return {
        "status": "no_pattern",
        "diagnosis": None,
        "confidence": "low",
        "alarm_code": None,
        "recommended_procedure": None,
        "escalation_required": critical_escalation,
        "escalation_procedure": (
            "MNT-MA-007"
            if critical_escalation
            else None
        ),
        "evidence": [],
        "message": (
            "The current sensor pattern does not match a documented "
            "multi-sensor diagnosis rule."
        ),
    }
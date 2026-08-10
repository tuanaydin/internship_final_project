from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
THRESHOLDS_FILE = PROJECT_ROOT / "config" / "thresholds.yaml"


SEVERITY_ORDER = {
    "normal": 0,
    "info": 1,
    "warning": 2,
    "critical": 3,
}


def load_thresholds() -> dict[str, Any]:
    """
    Sensör eşiklerini thresholds.yaml dosyasından yükler.
    """

    if not THRESHOLDS_FILE.exists():
        raise FileNotFoundError(
            f"Threshold configuration not found: {THRESHOLDS_FILE}"
        )

    with THRESHOLDS_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data:
        raise ValueError("thresholds.yaml is empty.")

    return data


def get_machine_thresholds(
    machine_id: str,
) -> dict[str, Any]:
    """
    Makineye ait eşik konfigürasyonunu döndürür.
    """

    thresholds = load_thresholds()

    machine_thresholds = (
        thresholds
        .get("machines", {})
        .get(machine_id)
    )

    if machine_thresholds is None:
        raise ValueError(
            f"Threshold configuration not found for: {machine_id}"
        )

    return machine_thresholds


def evaluate_standard_sensor(
    sensor_name: str,
    value: float | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Sıcaklık, titreşim ve akım gibi üst eşik mantığı
    kullanan sensörleri değerlendirir.
    """

    if value is None:
        return {
            "sensor": sensor_name,
            "value": None,
            "unit": config.get("unit"),
            "status": "unavailable",
            "alarm_code": None,
        }

    critical_min = config["critical_min"]
    warning_min = config["warning_min"]

    if value >= critical_min:
        status = "critical"
        alarm_code = config.get("critical_alarm")

    elif value >= warning_min:
        status = "warning"
        alarm_code = config.get("warning_alarm")

    else:
        status = "normal"
        alarm_code = None

    return {
        "sensor": sensor_name,
        "value": value,
        "unit": config.get("unit"),
        "status": status,
        "alarm_code": alarm_code,
    }


def evaluate_load(
    value: float | None,
    operating_state: str | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Motor yükünü çalışma durumunu dikkate alarak değerlendirir.
    """

    if value is None:
        return {
            "sensor": "load_pct",
            "value": None,
            "unit": "%",
            "status": "unavailable",
            "alarm_code": None,
        }

    # Motor çalışmıyorsa düşük yükü anomali saymıyoruz.
    if operating_state != "running":
        return {
            "sensor": "load_pct",
            "value": value,
            "unit": "%",
            "status": "not_evaluated",
            "alarm_code": None,
            "reason": f"Operating state is {operating_state}.",
        }

    if value >= config["critical_min"]:
        return {
            "sensor": "load_pct",
            "value": value,
            "unit": "%",
            "status": "critical",
            "alarm_code": config.get("critical_alarm"),
        }

    if value > config["warning_min"]:
        return {
            "sensor": "load_pct",
            "value": value,
            "unit": "%",
            "status": "warning",
            "alarm_code": config.get("warning_alarm"),
        }

    if value >= config["normal_min"]:
        return {
            "sensor": "load_pct",
            "value": value,
            "unit": "%",
            "status": "normal",
            "alarm_code": None,
        }

    # Doküman running durumda %35 altını açıkça
    # sınıflandırmadığı için bilgi uydurmuyoruz.
    return {
        "sensor": "load_pct",
        "value": value,
        "unit": "%",
        "status": "info",
        "alarm_code": None,
        "reason": "Value is below the documented normal load range.",
    }


def calculate_overall_status(
    results: list[dict[str, Any]],
) -> str:
    """
    Sensör sonuçlarından makinenin en yüksek önem seviyesini bulur.
    """

    evaluable_statuses = [
        result["status"]
        for result in results
        if result["status"] in SEVERITY_ORDER
    ]

    if not evaluable_statuses:
        return "unknown"

    return max(
        evaluable_statuses,
        key=lambda status: SEVERITY_ORDER[status],
    )


def analyze_measurement(
    machine_id: str,
    measurement: dict[str, Any],
) -> dict[str, Any]:
    """
    Tek bir makine ölçümünü eşiklere göre analiz eder.
    """

    thresholds = get_machine_thresholds(machine_id)

    results = []

    for sensor_name in [
        "temperature_c",
        "vibration_mm_s",
        "current_a",
    ]:
        result = evaluate_standard_sensor(
            sensor_name=sensor_name,
            value=measurement.get(sensor_name),
            config=thresholds[sensor_name],
        )

        results.append(result)

    load_result = evaluate_load(
        value=measurement.get("load_pct"),
        operating_state=measurement.get("operating_state"),
        config=thresholds["load_pct"],
    )

    results.append(load_result)

    overall_status = calculate_overall_status(results)

    active_alarms = [
        result["alarm_code"]
        for result in results
        if result.get("alarm_code") is not None
    ]

    return {
        "machine_id": machine_id,
        "timestamp": measurement.get("timestamp"),
        "operating_state": measurement.get("operating_state"),
        "overall_status": overall_status,
        "active_alarms": active_alarms,
        "sensor_analysis": results,
    }
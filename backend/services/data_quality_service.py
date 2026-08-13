from __future__ import annotations


from statistics import median
from typing import Any

import yaml


from backend.core.config import DATA_QUALITY_FILE

def load_data_quality_config() -> dict[str, Any]:
    if not DATA_QUALITY_FILE.exists():
        raise FileNotFoundError(
            f"Data quality config not found: {DATA_QUALITY_FILE}"
        )

    with DATA_QUALITY_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not data:
        raise ValueError(
            "data_quality.yaml is empty."
        )

    return data


def get_machine_data_quality_config(
    machine_id: str,
) -> dict[str, Any]:
    config = load_data_quality_config()

    machine_config = (
        config
        .get("machines", {})
        .get(machine_id)
    )

    if machine_config is None:
        raise ValueError(
            f"Data quality configuration not found for {machine_id}"
        )

    return machine_config


def detect_missing(
    latest: dict[str, Any],
    required_fields: list[str],
) -> dict[str, Any] | None:
    """
    Gerekli sensörlerden biri boşsa missing olayı oluşturur.
    """

    missing_fields = [
        field
        for field in required_fields
        if latest.get(field) is None
    ]

    if not missing_fields:
        return None

    return {
        "code": "DQ-MISS-01",
        "type": "missing",
        "severity": "medium",
        "affected_fields": missing_fields,
        "message": "Required sensor telemetry is missing.",
    }


def detect_stuck(
    measurements: list[dict[str, Any]],
    sensor_name: str,
    window_size: int,
) -> dict[str, Any] | None:
    """
    Sensörün belirli pencere boyunca tamamen aynı değerde
    kalıp kalmadığını kontrol eder.
    """

    if len(measurements) < window_size:
        return None

    window = measurements[-window_size:]

    sensor_values = [
        row.get(sensor_name)
        for row in window
    ]

    if any(value is None for value in sensor_values):
        return None

    unique_sensor_values = set(sensor_values)

    if len(unique_sensor_values) != 1:
        return None

    # Aynı sürede proses gerçekten değişmiş mi?
    load_values = [
        row.get("load_pct")
        for row in window
        if row.get("load_pct") is not None
    ]

    current_values = [
        row.get("current_a")
        for row in window
        if row.get("current_a") is not None
    ]

    load_changed = (
        len(set(load_values)) > 1
        if load_values
        else False
    )

    current_changed = (
        len(set(current_values)) > 1
        if current_values
        else False
    )

    if not load_changed and not current_changed:
        return None

    return {
        "code": "DQ-STUCK-01",
        "type": "stuck",
        "severity": "medium",
        "sensor": sensor_name,
        "value": sensor_values[-1],
        "window_size": window_size,
        "message": (
            "Sensor remained constant while "
            "operating conditions changed."
        ),
    }


def detect_suspected_spike(
    measurements: list[dict[str, Any]],
    sensor_name: str,
    comparison_window: int,
    deviation_threshold: float,
) -> dict[str, Any] | None:
    """
    Son ölçümün yakın geçmişten çok büyük sapma gösterip
    göstermediğini kontrol eder.

    Bu canlı analiz olduğu için sonuç 'suspected_spike'
    olarak ifade edilir. Bir sonraki ölçümle doğrulanabilir.
    """

    required_length = comparison_window + 1

    if len(measurements) < required_length:
        return None

    latest = measurements[-1]
    latest_value = latest.get(sensor_name)

    if latest_value is None:
        return None

    previous_rows = measurements[
        -(comparison_window + 1):-1
    ]

    previous_values = [
        row.get(sensor_name)
        for row in previous_rows
        if row.get(sensor_name) is not None
    ]

    if len(previous_values) < comparison_window:
        return None

    baseline = median(previous_values)

    deviation = abs(latest_value - baseline)

    if deviation < deviation_threshold:
        return None

    return {
        "code": "DQ-SPIKE-01",
        "type": "suspected_spike",
        "severity": "medium",
        "sensor": sensor_name,
        "value": latest_value,
        "baseline": round(baseline, 3),
        "deviation": round(deviation, 3),
        "message": (
            "Latest measurement differs strongly "
            "from recent sensor values."
        ),
    }


def analyze_data_quality(
    machine_id: str,
    measurements: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Son ölçüm penceresi için tüm veri kalitesi
    kontrollerini çalıştırır.
    """

    if not measurements:
        return {
            "status": "unknown",
            "issues": [],
        }

    config = get_machine_data_quality_config(
        machine_id
    )

    latest = measurements[-1]

    issues = []

    # Eksik veri kontrolü
    missing_issue = detect_missing(
        latest=latest,
        required_fields=config["required_fields"],
    )

    if missing_issue:
        issues.append(
            missing_issue
        )

    # Stuck sensör kontrolü
    # İlgili makine için config tanımlı değilse
    # bu kontrol atlanır.
    stuck_config = config.get(
        "stuck"
    )

    if stuck_config:
        stuck_issue = detect_stuck(
            measurements=measurements,
            sensor_name=stuck_config[
                "sensor"
            ],
            window_size=stuck_config[
                "window_size"
            ],
        )

        if stuck_issue:
            issues.append(
                stuck_issue
            )

    # Ani sıçrama kontrolü
    # İlgili makine için config tanımlı değilse
    # bu kontrol atlanır.
    spike_config = config.get(
        "spike"
    )

    if spike_config:
        spike_issue = detect_suspected_spike(
            measurements=measurements,
            sensor_name=spike_config[
                "sensor"
            ],
            comparison_window=spike_config[
                "comparison_window"
            ],
            deviation_threshold=spike_config[
                "deviation_threshold"
            ],
        )

        if spike_issue:
            issues.append(
                spike_issue
            )

    if issues:
        status = "unreliable"
    else:
        status = "ok"

    return {
        "status": status,
        "issues": issues,
    }
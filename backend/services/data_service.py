from __future__ import annotations
from pathlib import Path
import csv
from datetime import datetime,timedelta

from typing import Any

from backend.services.asset_service import get_machine
from backend.core.config import PROJECT_ROOT




# Uygulamanın analiz için kullanacağı ham IoT alanları
RAW_SENSOR_FIELDS = [
    "timestamp",
    "device_id",
    "operating_state",
    "load_pct",
    "temperature_c",
    "vibration_mm_s",
    "current_a",
    "power_kw",
    "energy_kwh_5min",
]


def get_sensor_data_path(machine_id: str) -> Path:
    """
    assets.yaml üzerinden makinenin sensör CSV yolunu bulur.
    """

    machine = get_machine(machine_id)

    if machine is None:
        raise ValueError(f"Machine not found: {machine_id}")

    data_config = machine.get("data", {})
    relative_path = data_config.get("sensor_data")

    if not relative_path:
        raise ValueError(
            f"Sensor data path is not defined for machine: {machine_id}"
        )

    sensor_path = PROJECT_ROOT / relative_path

    if not sensor_path.exists():
        raise FileNotFoundError(
            f"Sensor data file not found: {sensor_path}"
        )

    return sensor_path


def _parse_float(value: str | None) -> float | None:
    """
    CSV'deki sayısal alanları float'a dönüştürür.
    Eksik değer varsa None döndürür.
    """

    if value is None or value.strip() == "":
        return None

    return float(value)


def normalize_sensor_row(row: dict[str, str]) -> dict[str, Any]:
    """
    CSV satırını API'de kullanacağımız temiz veri yapısına dönüştürür.
    """

    return {
        "timestamp": row.get("timestamp"),
        "device_id": row.get("device_id"),
        "operating_state": row.get("operating_state"),
        "load_pct": _parse_float(row.get("load_pct")),
        "temperature_c": _parse_float(row.get("temperature_c")),
        "vibration_mm_s": _parse_float(row.get("vibration_mm_s")),
        "current_a": _parse_float(row.get("current_a")),
        "power_kw": _parse_float(row.get("power_kw")),
        "energy_kwh_5min": _parse_float(row.get("energy_kwh_5min")),
    }


def load_machine_sensor_data(
    machine_id: str,
) -> list[dict[str, Any]]:
    """
    Makinenin tüm ham sensör ölçümlerini CSV'den okur.
    """

    sensor_path = get_sensor_data_path(machine_id)

    measurements = []

    with sensor_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Güvenlik amacıyla yalnızca istenen makinenin
            # kayıtlarını alıyoruz.
            if row.get("device_id") != machine_id:
                continue

            measurements.append(
                normalize_sensor_row(row)
            )

    return measurements


def get_latest_measurement(
    machine_id: str,
) -> dict[str, Any] | None:
    """
    Makinenin en son sensör ölçümünü döndürür.
    """

    measurements = load_machine_sensor_data(machine_id)

    if not measurements:
        return None

    return max(
        measurements,
        key=lambda item: item["timestamp"],
    )


def get_recent_measurements(
    machine_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Makinenin en son N sensör ölçümünü kronolojik sırayla döndürür.
    """

    measurements = load_machine_sensor_data(machine_id)

    if not measurements:
        return []

    sorted_measurements = sorted(
        measurements,
        key=lambda item: item["timestamp"],
    )

    return sorted_measurements[-limit:]

def get_measurements_until(
    machine_id: str,
    timestamp: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Belirtilen timestamp'e kadar olan son N ölçümü döndürür.

    Bu fonksiyon geçmişteki olayların analiz edilmesi için kullanılır.
    """

    measurements = load_machine_sensor_data(machine_id)

    if not measurements:
        return []

    target_time = datetime.fromisoformat(timestamp)

    filtered_measurements = []

    for measurement in measurements:
        measurement_time = datetime.fromisoformat(
            measurement["timestamp"]
        )

        if measurement_time <= target_time:
            filtered_measurements.append(measurement)

    filtered_measurements.sort(
        key=lambda item: item["timestamp"]
    )

    return filtered_measurements[-limit:]

def get_measurements_in_window(
    machine_id: str,
    timestamp: str,
    window_minutes: int,
) -> list[dict[str, Any]]:
    """
    Belirtilen timestamp ile geçmişteki zaman penceresi
    arasında kalan sensör ölçümlerini kronolojik sırayla döndürür.

    Örnek:
    timestamp = 2026-07-27 20:00:00
    window_minutes = 300

    Aralık:
    2026-07-27 15:00:00
    ->
    2026-07-27 20:00:00
    """

    if window_minutes <= 0:
        raise ValueError(
            "window_minutes must be greater than zero."
        )

    measurements = load_machine_sensor_data(machine_id)

    if not measurements:
        return []

    target_time = datetime.fromisoformat(timestamp)

    start_time = target_time - timedelta(
        minutes=window_minutes
    )

    filtered_measurements = []

    for measurement in measurements:
        measurement_time = datetime.fromisoformat(
            measurement["timestamp"]
        )

        if start_time <= measurement_time <= target_time:
            filtered_measurements.append(measurement)

    filtered_measurements.sort(
        key=lambda item: item["timestamp"]
    )

    return filtered_measurements
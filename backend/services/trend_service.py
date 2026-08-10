from __future__ import annotations


from typing import Any


TREND_EPSILON = {
    "temperature_c": 1.0,
    "vibration_mm_s": 0.2,
    "current_a": 0.5,
    "load_pct": 2.0,
    "power_kw": 0.5,
}


def calculate_sensor_trend(
    measurements: list[dict[str, Any]],
    sensor_name: str,
) -> dict[str, Any]:
    """
    Bir sensörün verilen zaman penceresindeki değişimini hesaplar.
    """

    valid_measurements = [
        measurement
        for measurement in measurements
        if measurement.get(sensor_name) is not None
    ]

    if len(valid_measurements) < 2:
        return {
            "sensor": sensor_name,
            "status": "insufficient_data",
            "start_value": None,
            "end_value": None,
            "change": None,
            "direction": "unknown",
        }

    start_value = valid_measurements[0][sensor_name]
    end_value = valid_measurements[-1][sensor_name]

    change = end_value - start_value

    epsilon = TREND_EPSILON.get(sensor_name, 0.0)

    if change > epsilon:
        direction = "increasing"

    elif change < -epsilon:
        direction = "decreasing"

    else:
        direction = "stable"

    return {
        "sensor": sensor_name,
        "status": "ok",
        "start_value": round(start_value, 3),
        "end_value": round(end_value, 3),
        "change": round(change, 3),
        "direction": direction,
    }


def analyze_trends(
    measurements: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Temel Motor-A sensörlerinin trendlerini hesaplar.
    """

    if not measurements:
        return {
            "status": "unknown",
            "window_start": None,
            "window_end": None,
            "trends": [],
        }

    sensors = [
        "temperature_c",
        "vibration_mm_s",
        "current_a",
        "load_pct",
        "power_kw",
    ]

    trends = [
        calculate_sensor_trend(
            measurements=measurements,
            sensor_name=sensor,
        )
        for sensor in sensors
    ]

    return {
        "status": "ok",
        "window_start": measurements[0]["timestamp"],
        "window_end": measurements[-1]["timestamp"],
        "measurement_count": len(measurements),
        "trends": trends,
    }
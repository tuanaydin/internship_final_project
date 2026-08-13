from fastapi.testclient import TestClient
from backend.api.routes import analysis as analysis_routes

def test_measurement_window_is_time_based_and_inclusive(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/machines/MOTOR_A/measurements/at",
        params={
            "timestamp": "2026-07-27 20:00:00",
            "window_minutes": 300,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["machine_id"] == "MOTOR_A"
    assert body["requested_timestamp"] == "2026-07-27 20:00:00"
    assert body["window_minutes"] == 300
    assert body["measurement_count"] == len(body["measurements"])
    assert body["measurements"][0]["timestamp"] >= "2026-07-27 15:00:00"
    assert body["measurements"][-1]["timestamp"] == "2026-07-27 20:00:00"


def test_known_overload_event_keeps_deterministic_diagnosis(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/machines/MOTOR_A/diagnostics/at",
        params={
            "timestamp": "2026-07-12 10:30:00",
            "window_minutes": 150,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["machine_id"] == "MOTOR_A"
    assert body["measurement"]["load_pct"] == 95.74
    assert body["measurement"]["current_a"] == 23.37
    assert body["threshold_analysis"]["overall_status"] == "critical"
    assert body["data_quality"]["status"] == "ok"
    assert body["diagnosis"]["status"] == "diagnosed"
    assert body["diagnosis"]["diagnosis"] == "overload"
    assert body["diagnosis"]["escalation_required"] is True


def test_missing_sensor_event_marks_data_as_unreliable(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/machines/MOTOR_A/data-quality/at",
        params={"timestamp": "2026-07-23 13:40:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_quality"]["status"] == "unreliable"
    issue_codes = {
        issue["code"] for issue in body["data_quality"]["issues"]
    }
    assert "DQ-MISS-01" in issue_codes


def test_invalid_timestamp_keeps_existing_error_contract(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/machines/MOTOR_A/measurements/at",
        params={"timestamp": "not-a-timestamp", "window_minutes": 60},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS."
    }


def test_non_positive_window_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/v1/machines/MOTOR_A/diagnostics/at",
        params={
            "timestamp": "2026-07-12 10:30:00",
            "window_minutes": 0,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "window_minutes must be greater than zero."
    }


def test_unknown_machine_analysis_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/machines/UNKNOWN/analysis/latest")

    assert response.status_code == 404
    assert response.json() == {"detail": "Machine not found."}



def test_trends_and_diagnostics_use_time_based_window(
    client,
    monkeypatch,
) -> None:
    """
    Trend ve diagnostik endpointlerinin kayıt sayısı
    varsayımı yerine gerçek zaman penceresini
    kullandığını doğrular.
    """

    original_function = (
        analysis_routes.get_measurements_in_window
    )

    calls = []

    def spy_get_measurements_in_window(
        machine_id: str,
        timestamp: str,
        window_minutes: int,
    ):
        calls.append(
            (
                machine_id,
                timestamp,
                window_minutes,
            )
        )

        return original_function(
            machine_id=machine_id,
            timestamp=timestamp,
            window_minutes=window_minutes,
        )

    monkeypatch.setattr(
            analysis_routes,
            "get_measurements_in_window",
            spy_get_measurements_in_window,
        )

    timestamp = "2026-07-27 20:00:00"
    window_minutes = 300

    trends_response = client.get(
        "/api/v1/machines/MOTOR_A/trends/at",
        params={
            "timestamp": timestamp,
            "window_minutes": window_minutes,
        },
    )

    diagnostics_response = client.get(
        "/api/v1/machines/MOTOR_A/diagnostics/at",
        params={
            "timestamp": timestamp,
            "window_minutes": window_minutes,
        },
    )

    assert trends_response.status_code == 200
    assert diagnostics_response.status_code == 200

    assert calls == [
        (
            "MOTOR_A",
            timestamp,
            window_minutes,
        ),
        (
            "MOTOR_A",
            timestamp,
            window_minutes,
        ),
    ]
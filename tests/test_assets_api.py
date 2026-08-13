from fastapi.testclient import TestClient


def test_plant_detail_preserves_identity(client: TestClient) -> None:
    response = client.get("/api/v1/plants/PLANT_01")

    assert response.status_code == 200
    assert response.json() == {
        "id": "PLANT_01",
        "name": "Demo Factory",
    }


def test_station_list_preserves_current_hierarchy(client: TestClient) -> None:
    response = client.get("/api/v1/plants/PLANT_01/stations")

    assert response.status_code == 200
    stations = response.json()
    assert [station["id"] for station in stations] == [
        "STATION_01",
        "STATION_02",
    ]
    assert all(station["plant_id"] == "PLANT_01" for station in stations)


def test_station_machine_list_contains_motor_a(client: TestClient) -> None:
    response = client.get("/api/v1/stations/STATION_01/machines")

    assert response.status_code == 200
    machines = response.json()
    assert [machine["id"] for machine in machines] == ["MOTOR_A"]
    assert machines[0]["name"] == "Motor A"
    assert machines[0]["type"] == "electric_motor"


def test_machine_detail_includes_parent_ids(client: TestClient) -> None:
    response = client.get("/api/v1/machines/MOTOR_A")

    assert response.status_code == 200
    machine = response.json()
    assert machine["id"] == "MOTOR_A"
    assert machine["plant_id"] == "PLANT_01"
    assert machine["station_id"] == "STATION_01"
    assert {sensor["type"] for sensor in machine["sensors"]} == {
        "temperature",
        "vibration",
        "current",
        "active_power",
    }


def test_unknown_assets_keep_existing_404_contract(client: TestClient) -> None:
    cases = [
        ("/api/v1/plants/UNKNOWN", "Plant not found."),
        ("/api/v1/stations/UNKNOWN", "Station not found."),
        ("/api/v1/machines/UNKNOWN", "Machine not found."),
    ]

    for path, expected_detail in cases:
        response = client.get(path)

        assert response.status_code == 404
        assert response.json() == {"detail": expected_detail}


def test_plant_hierarchy_contains_station_and_machine(
    client,
) -> None:
    response = client.get(
        "/api/v1/plants/PLANT_01/hierarchy"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "PLANT_01"
    assert data["name"] == "Demo Factory"

    stations = data["stations"]

    station_01 = next(
        station
        for station in stations
        if station["id"] == "STATION_01"
    )

    assert (
        station_01["plant_id"]
        == "PLANT_01"
    )

    machines = station_01["machines"]

    motor_a = next(
        machine
        for machine in machines
        if machine["id"] == "MOTOR_A"
    )

    assert motor_a["name"] == "Motor A"
    assert (
        motor_a["type"]
        == "electric_motor"
    )

    # Spatial bilgi henüz assets.yaml
    # içerisine eklenmedi.
    assert motor_a["spatial"] == {
    "x_pct": 68.0,
    "y_pct": 42.0,
    }


def test_unknown_plant_hierarchy_returns_404(
    client,
) -> None:
    response = client.get(
        "/api/v1/plants/UNKNOWN_PLANT/hierarchy"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Plant not found."
    }
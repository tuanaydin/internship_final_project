from backend.services.asset_catalog import (
    get_asset_catalog,
)
from backend.services.asset_service import (
    get_machine_by_id,
    list_machines,
)


def test_asset_catalog_is_cached() -> None:
    first_catalog = get_asset_catalog()
    second_catalog = get_asset_catalog()

    assert first_catalog is second_catalog


def test_service_results_cannot_mutate_cached_catalog() -> None:
    machine = get_machine_by_id(
        "MOTOR_A"
    )

    assert machine is not None

    machine["name"] = "Changed in test"

    fresh_machine = get_machine_by_id(
        "MOTOR_A"
    )

    assert fresh_machine is not None
    assert (
        fresh_machine["name"]
        == "Motor A"
    )


def test_machine_list_returns_machines_for_station() -> None:
    machines = list_machines(
        station_id="STATION_01"
    )

    assert [
        machine["id"]
        for machine in machines
    ] == ["MOTOR_A"]
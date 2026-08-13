from __future__ import annotations

from copy import deepcopy
from typing import Any

from backend.services.asset_catalog import (
    get_asset_catalog,
)


def get_plant_by_id(
    plant_id: str,
) -> dict[str, Any] | None:
    plant = (
        get_asset_catalog()
        .plants_by_id
        .get(plant_id)
    )

    return (
        deepcopy(plant)
        if plant is not None
        else None
    )


def get_station_by_id(
    station_id: str,
) -> dict[str, Any] | None:
    station = (
        get_asset_catalog()
        .stations_by_id
        .get(station_id)
    )

    return (
        deepcopy(station)
        if station is not None
        else None
    )


def get_machine_by_id(
    machine_id: str,
) -> dict[str, Any] | None:
    machine = (
        get_asset_catalog()
        .machines_by_id
        .get(machine_id)
    )

    return (
        deepcopy(machine)
        if machine is not None
        else None
    )


def list_stations(
    plant_id: str | None = None,
) -> list[dict[str, Any]]:
    catalog = get_asset_catalog()

    if plant_id is None:
        stations = list(
            catalog.stations_by_id.values()
        )
    else:
        stations = (
            catalog
            .stations_by_plant_id
            .get(plant_id, [])
        )

    return deepcopy(stations)


def list_machines(
    station_id: str | None = None,
) -> list[dict[str, Any]]:
    catalog = get_asset_catalog()

    if station_id is None:
        machines = list(
            catalog.machines_by_id.values()
        )
    else:
        machines = (
            catalog
            .machines_by_station_id
            .get(station_id, [])
        )

    return deepcopy(machines)


# ---------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------
# Downstream servisleri yeni isimlere geçirene kadar
# mevcut import sözleşmelerini koruyoruz.
"""

def get_plant(
    plant_id: str,
) -> dict[str, Any] | None:
    return get_plant_by_id(plant_id)


def get_station(
    station_id: str,
) -> dict[str, Any] | None:
    return get_station_by_id(station_id)


def get_machine(
    machine_id: str,
) -> dict[str, Any] | None:
    return get_machine_by_id(machine_id)


def get_stations(
    plant_id: str,
) -> list[dict[str, Any]]:
    return list_stations(
        plant_id=plant_id
    )


def get_machines(
    station_id: str,
) -> list[dict[str, Any]]:
    return list_machines(
        station_id=station_id
    )
"""
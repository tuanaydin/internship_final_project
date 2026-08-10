from __future__ import annotations
from typing import Any

import yaml

from backend.core.config import ASSETS_FILE

def load_assets() -> dict[str, Any]:
    """
    assets.yaml dosyasını okuyup Python dictionary olarak döndürür.
    """

    if not ASSETS_FILE.exists():
        raise FileNotFoundError(
            f"Asset configuration file not found: {ASSETS_FILE}"
        )

    with ASSETS_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data:
        raise ValueError("assets.yaml is empty.")

    return data


def get_plant(plant_id: str) -> dict[str, Any] | None:
    """
    ID'ye göre plant bilgisini döndürür.
    """

    assets = load_assets()
    plant = assets.get("plant")

    if plant and plant.get("id") == plant_id:
        return plant

    return None


def get_stations(plant_id: str) -> list[dict[str, Any]]:
    """
    Belirtilen plant altındaki istasyonları döndürür.
    """

    assets = load_assets()

    return [
        station
        for station in assets.get("stations", [])
        if station.get("plant_id") == plant_id
    ]


def get_station(station_id: str) -> dict[str, Any] | None:
    """
    ID'ye göre istasyonu döndürür.
    """

    assets = load_assets()

    for station in assets.get("stations", []):
        if station.get("id") == station_id:
            return station

    return None


def get_machines(station_id: str) -> list[dict[str, Any]]:
    """
    Belirtilen istasyondaki makineleri döndürür.
    """

    station = get_station(station_id)

    if station is None:
        return []

    return station.get("machines", [])


def get_machine(machine_id: str) -> dict[str, Any] | None:
    """
    Tüm istasyonlar içerisinde makineyi ID'ye göre arar.
    """

    assets = load_assets()

    for station in assets.get("stations", []):
        for machine in station.get("machines", []):
            if machine.get("id") == machine_id:
                return {
                    **machine,
                    "station_id": station.get("id"),
                    "plant_id": station.get("plant_id"),
                }

    return None
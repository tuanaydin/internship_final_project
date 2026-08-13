from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import yaml

from backend.core.config import ASSETS_FILE


class InvalidAssetConfigurationError(ValueError):
    """assets.yaml içinde geçersiz bir hiyerarşi olduğunda yükseltilir."""


@dataclass(frozen=True)
class AssetCatalog:
    plants_by_id: dict[str, dict[str, Any]]
    stations_by_id: dict[str, dict[str, Any]]
    machines_by_id: dict[str, dict[str, Any]]
    stations_by_plant_id: dict[str, list[dict[str, Any]]]
    machines_by_station_id: dict[str, list[dict[str, Any]]]


def _require_unique_id(
    index: dict[str, dict[str, Any]],
    asset: dict[str, Any],
    asset_type: str,
) -> str:
    asset_id = asset.get("id")

    if not asset_id:
        raise InvalidAssetConfigurationError(
            f"{asset_type} id'si gerekli."
        )

    if asset_id in index:
        raise InvalidAssetConfigurationError(
            f"Duplicate {asset_type} id: {asset_id}"
        )

    return asset_id


def _build_catalog(
    data: dict[str, Any],
) -> AssetCatalog:
    plant = data.get("plant")

    if not isinstance(plant, dict):
        raise InvalidAssetConfigurationError(
            "assets.yaml bir tesis tanımlamalıdır."
        )

    plant_id = plant.get("id")

    if not plant_id:
        raise InvalidAssetConfigurationError(
            "Tesis id zorunludur."
        )

    stations = data.get("stations", [])

    if not isinstance(stations, list):
        raise InvalidAssetConfigurationError(
            "stations bir liste olmalıdır."
        )

    plants_by_id = {
        plant_id: plant,
    }

    stations_by_id: dict[
        str,
        dict[str, Any],
    ] = {}

    machines_by_id: dict[
        str,
        dict[str, Any],
    ] = {}

    stations_by_plant_id: dict[
        str,
        list[dict[str, Any]],
    ] = {
        plant_id: [],
    }

    machines_by_station_id: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for station in stations:
        if not isinstance(station, dict):
            raise InvalidAssetConfigurationError(
                "Her istasyon bir eşleme (mapping) olmalıdır."
            )

        station_id = _require_unique_id(
            stations_by_id,
            station,
            "station",
        )

        station_plant_id = station.get(
            "plant_id"
        )

        if station_plant_id not in plants_by_id:
            raise InvalidAssetConfigurationError(
                f"Bilinmeyen plant_id "
                f"'{station_plant_id}' "
                f"için istasyon '{station_id}'."
            )

        stations_by_id[
            station_id
        ] = station

        stations_by_plant_id.setdefault(
            station_plant_id,
            [],
        ).append(station)

        machines_by_station_id[
            station_id
        ] = []

        machines = station.get(
            "machines",
            [],
        )

        if not isinstance(machines, list):
            raise InvalidAssetConfigurationError(
                "machines bir liste olmalıdır "
                f"istasyon '{station_id}' için."
            )

        for machine in machines:
            if not isinstance(machine, dict):
                raise InvalidAssetConfigurationError(
                    "Her makine istasyon "
                    f"'{station_id}' içinde bir eşleme (mapping) olmalıdır."
                )

            machine_id = _require_unique_id(
                machines_by_id,
                machine,
                "machine",
            )

            indexed_machine = {
                **machine,
                "station_id": station_id,
                "plant_id": station_plant_id,
            }

            machines_by_id[
                machine_id
            ] = indexed_machine

            machines_by_station_id[
                station_id
            ].append(indexed_machine)

    return AssetCatalog(
        plants_by_id=plants_by_id,
        stations_by_id=stations_by_id,
        machines_by_id=machines_by_id,
        stations_by_plant_id=(
            stations_by_plant_id
        ),
        machines_by_station_id=(
            machines_by_station_id
        ),
    )


@lru_cache(maxsize=1)
def get_asset_catalog() -> AssetCatalog:
    """
    assets.yaml dosyasını yükler, doğrular ve
    süreç boyunca bir kez indeksler.
    """

    if not ASSETS_FILE.exists():
        raise FileNotFoundError(
            "Asset yapılandırma dosyası "
            f"bulunamadı: {ASSETS_FILE}"
        )

    with ASSETS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not data:
        raise InvalidAssetConfigurationError(
            "assets.yaml boş"
        )

    if not isinstance(data, dict):
        raise InvalidAssetConfigurationError(
            "assets.yaml kökü bir eşleme (mapping) olmalı"
        )

    return _build_catalog(data)


def clear_asset_catalog_cache() -> None:
    """
    Testler veya yeniden yüklenen açık yapılandırmalar için katalog önbelleğini temizler.
    """

    get_asset_catalog.cache_clear()
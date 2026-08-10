from fastapi import APIRouter, HTTPException

from backend.services.asset_service import (
    get_machines,
    get_plant,
    get_station,
    get_stations,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Assets"],
)


@router.get("/plants/{plant_id}")
def plant_detail(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return plant


@router.get("/plants/{plant_id}/stations")
def plant_stations(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return get_stations(plant_id)


@router.get("/stations/{station_id}")
def station_detail(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


@router.get("/stations/{station_id}/machines")
def station_machines(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return get_machines(station_id)
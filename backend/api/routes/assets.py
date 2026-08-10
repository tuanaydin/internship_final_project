from fastapi import APIRouter, HTTPException

from backend.services.asset_service import (
    get_machines,
    get_plant,
    get_station,
    get_stations,
)
from backend.schemas.asset import (
    MachineSchema,
    PlantSchema,
    StationSchema,
)


router = APIRouter(prefix="/api/v1",tags=["Assets"],)


@router.get("/plants/{plant_id}",response_model=PlantSchema,)
def plant_detail(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return plant


@router.get("/plants/{plant_id}/stations",response_model=list[StationSchema],)
def plant_stations(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return get_stations(plant_id)


@router.get("/stations/{station_id}", response_model=StationSchema,)
def station_detail(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


@router.get("/stations/{station_id}/machines",response_model=list[MachineSchema],)
def station_machines(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return get_machines(station_id)
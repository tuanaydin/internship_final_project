from fastapi import APIRouter, HTTPException

from backend.services.asset_service import get_machine
from backend.services.data_service import get_latest_measurement


router = APIRouter(
    prefix="/api/v1",
    tags=["Machines"],
)


@router.get("/machines/{machine_id}")
def machine_detail(machine_id: str):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    return machine


@router.get("/machines/{machine_id}/latest")
def machine_latest_measurement(machine_id: str):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    try:
        measurement = get_latest_measurement(machine_id)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor measurements found.",
        )

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "measurement": measurement,
    }
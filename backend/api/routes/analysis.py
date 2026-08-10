from fastapi import APIRouter, HTTPException

from backend.services.anomaly_service import analyze_measurement
from backend.services.asset_service import get_machine
from backend.services.data_quality_service import analyze_data_quality

from backend.services.data_service import (
    get_latest_measurement,
    get_recent_measurements,
)
from backend.schemas.analysis import (
    LatestAnalysisResponse,
    LatestDataQualityResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Analysis"],
)


@router.get("/machines/{machine_id}/analysis/latest",response_model=LatestAnalysisResponse,)
def machine_latest_analysis(machine_id: str):
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

    analysis = analyze_measurement(
        machine_id=machine_id,
        measurement=measurement,
    )

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        **analysis,
    }


@router.get("/machines/{machine_id}/data-quality/latest",response_model=LatestDataQualityResponse,)
def machine_latest_data_quality(machine_id: str):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    try:
        measurements = get_recent_measurements(
            machine_id=machine_id,
            limit=20,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No sensor measurements found.",
        )

    result = analyze_data_quality(
        machine_id=machine_id,
        measurements=measurements,
    )

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "timestamp": measurements[-1]["timestamp"],
        "data_quality": result,
    }
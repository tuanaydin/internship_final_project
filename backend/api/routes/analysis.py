from fastapi import APIRouter, HTTPException

from backend.services.anomaly_service import analyze_measurement
from backend.services.asset_service import get_machine
from backend.services.data_quality_service import analyze_data_quality
from backend.services.trend_service import analyze_trends
from backend.services.diagnostic_service import diagnose_machine

from backend.services.data_service import (
    get_latest_measurement,
    get_measurements_until,
    get_recent_measurements,
    get_measurements_in_window,

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

@router.get(
    "/machines/{machine_id}/data-quality/at"
)
def machine_data_quality_at(
    machine_id: str,
    timestamp: str,
):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    try:
        measurements = get_measurements_until(
            machine_id=machine_id,
            timestamp=timestamp,
            limit=20,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid timestamp format. "
                "Use YYYY-MM-DD HH:MM:SS."
            ),
        )

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No measurements found before this timestamp.",
        )

    result = analyze_data_quality(
        machine_id=machine_id,
        measurements=measurements,
    )

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "requested_timestamp": timestamp,
        "measurement": measurements[-1],
        "data_quality": result,
    }


@router.get(
    "/machines/{machine_id}/trends/at"
)
def machine_trends_at(
    machine_id: str,
    timestamp: str,
    window_minutes: int = 60,
):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    if window_minutes <= 0:
        raise HTTPException(
            status_code=400,
            detail="window_minutes must be greater than zero.",
        )

    measurement_limit = (window_minutes // 5) + 1

    try:
        measurements = get_measurements_until(
            machine_id=machine_id,
            timestamp=timestamp,
            limit=measurement_limit,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid timestamp format. "
                "Use YYYY-MM-DD HH:MM:SS."
            ),
        )

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No measurements found.",
        )

    trends = analyze_trends(measurements)

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "requested_timestamp": timestamp,
        "window_minutes": window_minutes,
        "trend_analysis": trends,
    }

@router.get(
    "/machines/{machine_id}/diagnostics/at"
)
def machine_diagnostics_at(
    machine_id: str,
    timestamp: str,
    window_minutes: int = 60,
):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    if window_minutes <= 0:
        raise HTTPException(
            status_code=400,
            detail="window_minutes must be greater than zero.",
        )

    measurement_limit = (window_minutes // 5) + 1

    try:
        measurements = get_measurements_until(
            machine_id=machine_id,
            timestamp=timestamp,
            limit=measurement_limit,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid timestamp format. "
                "Use YYYY-MM-DD HH:MM:SS."
            ),
        )

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No measurements found.",
        )

    latest_measurement = measurements[-1]

    threshold_analysis = analyze_measurement(
    machine_id=machine_id,
    measurement=latest_measurement,
)

    data_quality = analyze_data_quality(
        machine_id=machine_id,
        measurements=measurements,
    )

    trend_analysis = analyze_trends(
        measurements
    )

    diagnosis = diagnose_machine(
    measurement=latest_measurement,
    trend_analysis=trend_analysis,
    data_quality=data_quality,
    threshold_analysis=threshold_analysis,
)

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "requested_timestamp": timestamp,
        "window_minutes": window_minutes,
        "measurement": latest_measurement,
        "data_quality": data_quality,
        "trend_analysis": trend_analysis,
        "threshold_analysis": threshold_analysis,
        "diagnosis": diagnosis,
    }

@router.get(
    "/machines/{machine_id}/measurements/at"
)
def machine_measurements_at(
    machine_id: str,
    timestamp: str,
    window_minutes: int = 60,
):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    if window_minutes <= 0:
        raise HTTPException(
            status_code=400,
            detail="window_minutes must be greater than zero.",
        )

    try:
        measurements = get_measurements_in_window(
            machine_id=machine_id,
            timestamp=timestamp,
            window_minutes=window_minutes,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid timestamp format. "
                "Use YYYY-MM-DD HH:MM:SS."
            ),
        )

    if not measurements:
        raise HTTPException(
            status_code=404,
            detail="No measurements found in this time window.",
        )

    return {
        "plant_id": machine["plant_id"],
        "station_id": machine["station_id"],
        "machine_id": machine_id,
        "requested_timestamp": timestamp,
        "window_minutes": window_minutes,
        "measurement_count": len(measurements),
        "measurements": measurements,
    }
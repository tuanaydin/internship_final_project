from fastapi import FastAPI, HTTPException

from backend.services.asset_service import (
    get_machine,
    get_machines,
    get_plant,
    get_station,
    get_stations,
)


from backend.services.anomaly_service import (
    analyze_measurement,
)

from backend.services.data_service import (
    get_latest_measurement,
    get_recent_measurements,
)

from backend.services.data_quality_service import (
    analyze_data_quality,
)


app = FastAPI(
    title="Platform360 IoT Assistant API",
    description="IoT monitoring and maintenance decision support backend.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Platform360 IoT Assistant API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/api/v1/plants/{plant_id}")
def plant_detail(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return plant


@app.get("/api/v1/plants/{plant_id}/stations")
def plant_stations(plant_id: str):
    plant = get_plant(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return get_stations(plant_id)


@app.get("/api/v1/stations/{station_id}")
def station_detail(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


@app.get("/api/v1/stations/{station_id}/machines")
def station_machines(station_id: str):
    station = get_station(station_id)

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return get_machines(station_id)


@app.get("/api/v1/machines/{machine_id}")
def machine_detail(machine_id: str):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    return machine


@app.get("/api/v1/machines/{machine_id}/latest")
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

@app.get("/api/v1/machines/{machine_id}/analysis/latest")
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


@app.get(
    "/api/v1/machines/{machine_id}/data-quality/latest"
)
def machine_latest_data_quality(
    machine_id: str,
):
    machine = get_machine(machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    measurements = get_recent_measurements(
        machine_id=machine_id,
        limit=20,
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
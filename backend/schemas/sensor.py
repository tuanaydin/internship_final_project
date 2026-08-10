from __future__ import annotations

from pydantic import BaseModel


class SensorMeasurementSchema(BaseModel):
    timestamp: str
    device_id: str
    operating_state: str | None

    load_pct: float | None
    temperature_c: float | None
    vibration_mm_s: float | None
    current_a: float | None
    power_kw: float | None
    energy_kwh_5min: float | None


class LatestMeasurementResponse(BaseModel):
    plant_id: str
    station_id: str
    machine_id: str
    measurement: SensorMeasurementSchema
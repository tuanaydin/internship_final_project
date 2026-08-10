from __future__ import annotations

from pydantic import BaseModel, Field


class SensorAnalysisSchema(BaseModel):
    sensor: str
    value: float | None
    unit: str | None
    status: str
    alarm_code: str | None = None
    reason: str | None = None


class LatestAnalysisResponse(BaseModel):
    plant_id: str
    station_id: str

    machine_id: str
    timestamp: str | None
    operating_state: str | None

    overall_status: str
    active_alarms: list[str] = Field(default_factory=list)

    sensor_analysis: list[SensorAnalysisSchema] = Field(
        default_factory=list
    )


class DataQualityIssueSchema(BaseModel):
    code: str
    type: str
    severity: str

    sensor: str | None = None
    value: float | None = None

    affected_fields: list[str] | None = None

    window_size: int | None = None

    baseline: float | None = None
    deviation: float | None = None

    message: str


class DataQualityResultSchema(BaseModel):
    status: str
    issues: list[DataQualityIssueSchema] = Field(
        default_factory=list
    )


class LatestDataQualityResponse(BaseModel):
    plant_id: str
    station_id: str
    machine_id: str
    timestamp: str

    data_quality: DataQualityResultSchema
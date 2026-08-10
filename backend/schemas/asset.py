from __future__ import annotations

from pydantic import BaseModel, Field


class SensorDefinition(BaseModel):
    id: str
    type: str
    unit: str


class MachineDataConfig(BaseModel):
    sensor_data: str
    reference_dataset: str


class KnowledgeBaseConfig(BaseModel):
    path: str


class MachineSchema(BaseModel):
    id: str
    name: str
    type: str

    data: MachineDataConfig
    knowledge_base: KnowledgeBaseConfig
    sensors: list[SensorDefinition] = Field(default_factory=list)

    # get_machine() tarafından ekleniyor.
    station_id: str | None = None
    plant_id: str | None = None


class StationSchema(BaseModel):
    id: str
    name: str
    plant_id: str
    machines: list[MachineSchema] = Field(default_factory=list)


class PlantSchema(BaseModel):
    id: str
    name: str
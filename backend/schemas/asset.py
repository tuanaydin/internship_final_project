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

class SpatialPosition(BaseModel):
    """
    Makinenin fabrika layout'u üzerindeki
    yüzdesel konumunu temsil eder.
    """

    x_pct: float = Field(
        ge=0,
        le=100,
    )

    y_pct: float = Field(
        ge=0,
        le=100,
    )


class MachineSchema(BaseModel):
    id: str
    name: str
    type: str

    data: MachineDataConfig
    knowledge_base: KnowledgeBaseConfig
    sensors: list[SensorDefinition] = Field(default_factory=list)

    # get_machine_id() tarafından ekleniyor.
    station_id: str | None = None
    plant_id: str | None = None


    # Heat Map aşamasında kullanılacak.
    # Mevcut makinelerde tanımlı olmak zorunda değildir.
    spatial: SpatialPosition | None = None

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

# ---------------------------------------------------------
# Frontend hierarchy modelleri
# ---------------------------------------------------------


class MachineSummary(BaseModel):
    """
    Asset hierarchy ve fabrika layout'u için
    gerekli minimum makine bilgisini taşır.
    """

    id: str
    name: str
    type: str

    spatial: SpatialPosition | None = None


class StationHierarchy(BaseModel):
    """
    Bir istasyonu ve o istasyondaki makinelerin
    özet bilgilerini temsil eder.
    """

    id: str
    name: str
    plant_id: str

    machines: list[MachineSummary] = Field(
        default_factory=list
    )


class PlantHierarchy(BaseModel):
    """
    Plant → Station → Machine hiyerarşisini
    tek response içerisinde temsil eder.
    """

    id: str
    name: str

    stations: list[StationHierarchy] = Field(
        default_factory=list
    )
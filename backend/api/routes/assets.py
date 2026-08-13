from fastapi import APIRouter, HTTPException

from backend.schemas.asset import (
    MachineSchema,
    MachineSummary,
    PlantSchema,
    StationSchema,
    StationHierarchy,
    PlantHierarchy,
)
from backend.services.asset_service import (
    get_plant_by_id,
    get_station_by_id,
    list_machines,
    list_stations,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Assets"],
)


@router.get("/plants/{plant_id}",response_model=PlantSchema,)
def plant_detail(plant_id: str):
    """
    ID bilgisine göre plant detayını döndürür.
    """

    plant = get_plant_by_id(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return plant


@router.get(
    "/plants/{plant_id}/stations",
    response_model=list[StationSchema],
)
def plant_stations(plant_id: str):
    """
    Belirtilen plant altındaki istasyonları döndürür.
    """

    plant = get_plant_by_id(plant_id)

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    return list_stations(
        plant_id=plant_id
    )

###Heat Map aşamasında kullanılacak. Mevcut makinelerde tanımlı olmak zorunda değildir.
@router.get(
    "/plants/{plant_id}/hierarchy",
    response_model=PlantHierarchy,
)
def plant_hierarchy(
    plant_id: str,
):
    """
    Plant → Station → Machine hiyerarşisini
    frontend için tek response içerisinde döndürür.
    """

    plant = get_plant_by_id(
        plant_id
    )

    if plant is None:
        raise HTTPException(
            status_code=404,
            detail="Plant not found.",
        )

    stations = list_stations(
        plant_id=plant_id
    )

    station_hierarchy = []

    for station in stations:
        station_id = station["id"]

        machines = list_machines(
            station_id=station_id
        )

        machine_summaries = [
            MachineSummary(
                id=machine["id"],
                name=machine["name"],
                type=machine["type"],
                spatial=machine.get(
                    "spatial"
                ),
            )
            for machine in machines
        ]

        station_hierarchy.append(
            StationHierarchy(
                id=station["id"],
                name=station["name"],
                plant_id=station[
                    "plant_id"
                ],
                machines=machine_summaries,
            )
        )

    return PlantHierarchy(
        id=plant["id"],
        name=plant["name"],
        stations=station_hierarchy,
    )




@router.get("/stations/{station_id}",response_model=StationSchema,)
def station_detail(station_id: str):
    """
    ID bilgisine göre station detayını döndürür.
    """

    station = get_station_by_id(
        station_id
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return station


@router.get(
    "/stations/{station_id}/machines",
    response_model=list[MachineSchema],
)
def station_machines(station_id: str):
    """
    Belirtilen station altındaki makineleri döndürür.
    """

    station = get_station_by_id(
        station_id
    )

    if station is None:
        raise HTTPException(
            status_code=404,
            detail="Station not found.",
        )

    return list_machines(
        station_id=station_id
    )
from dataclasses import dataclass

from cartographer.models.enums import UnitType


@dataclass
class Unit:
    id: int
    region_id: int
    unit_type: UnitType
    owner: int | None = None

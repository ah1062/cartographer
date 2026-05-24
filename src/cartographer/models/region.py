from __future__ import annotations

from dataclasses import dataclass, field

from shapely.geometry.base import BaseGeometry

from cartographer.models.enums import RegionFlags, RegionType


@dataclass
class Region:
    id: int
    name: str

    geometry: BaseGeometry | None = None

    owner: int | None = None
    region_type: RegionType = RegionType.LAND
    region_flags: RegionFlags = RegionFlags.NONE
    supply_center: bool = False

    metadata: dict = field(default_factory=dict)

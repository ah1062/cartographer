from __future__ import annotations

from dataclasses import dataclass, field

from matplotlib.cm import get_cmap
from shapely.geometry.base import BaseGeometry

from cartographer.models.enums import RegionFlags, RegionType


@dataclass
class Region:
    id: int
    name: str

    geometry: BaseGeometry | None = None
    elevation: float = 0.0

    owner: int | None = None
    region_type: RegionType = RegionType.LAND
    region_flags: RegionFlags = RegionFlags.NONE
    supply_center: bool = False

    metadata: dict = field(default_factory=dict)

    def get_colour(self, elevation: bool = False) -> str | tuple[int, int, int]:
        region_colour = "pink"

        if elevation:
            r,g,b,a = get_cmap("viridis")(self.elevation)
            return (int(r*255), int(g*255), int(b*255))

        match self.region_type:
            case RegionType.LAND:
                region_colour = "lavender"
            case RegionType.SEA:
                region_colour = "lightsteelblue"
            case RegionType.DEEPSEA:
                region_colour = "steelblue"

        return region_colour

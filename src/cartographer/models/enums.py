from enum import Enum, Flag, auto


class RegionType(Enum):
    LAND = auto()
    SEA = auto()
    DEEPSEA = auto()
    LAKE = auto()

class RegionFlags(Flag):
    NONE = 0
    COAST = auto()
    RIVER = auto()
    LAKE = auto()
    MOUNTAIN = auto()

class UnitType(Enum):
    ARMY = auto()
    FLEET = auto()
    AIR = auto()  # optional future extension

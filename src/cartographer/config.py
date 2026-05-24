# cartographer/config.py

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from cartographer.utils import func_timer

# ============================================================
# WORLD
# ============================================================


@dataclass(slots=True)
class WorldConfig:
    width: int = 10000
    height: int = 10000
    point_count: int = 5000
    seed: int = 42


# ============================================================
# VORONOI
# ============================================================


@dataclass(slots=True)
class VoronoiConfig:
    relaxation_iterations: int = 2


# ============================================================
# SEA
# ============================================================


@dataclass(slots=True)
class SeaConfig:
    sea_ratio: float = 0.35
    deepsea_minimum_size: int = 5


# ============================================================
# EROSION
# ============================================================


@dataclass(slots=True)
class ErosionConfig:
    enabled: bool = True

    # number of erosion simulation passes
    iterations: int = 2

    # exponential decay factor
    # larger => softer continental interiors
    falloff: float = 3.5

    # overall erosion probability multiplier
    erosion_strength: float = 0.75

    # guaranteed protected inland core
    preserve_core_distance: int = 6


# ============================================================
# LAKES
# ============================================================


@dataclass(slots=True)
class LakeConfig:
    enabled: bool = True

    # poisson mean for number of lakes
    poisson_mean: float = 12

    # poisson mean for lake growth size
    average_size: float = 6

    # hard upper bound
    max_size: int = 30

    # minimum graph distance from sea
    min_inland_distance: int = 4


# ============================================================
# CLEANUP
# ============================================================


@dataclass(slots=True)
class CleanupConfig:
    enabled: bool = True

    # region minimum area as fraction of total world area
    min_area_fraction: float = 1e-5


# ============================================================
# RENDERER
# ============================================================


@dataclass(slots=True)
class RendererConfig:
    background: tuple[int, int, int] = (255, 255, 255)
    edge_colour: tuple[int, int, int] = (0, 0, 0)
    edge_width: int = 1
    border_size: int = 30
    border_colour: tuple[int, int, int] = (105, 70, 30)


# ============================================================
# ROOT CONFIG
# ============================================================


@dataclass(slots=True)
class Config:
    world: WorldConfig
    voronoi: VoronoiConfig
    sea: SeaConfig
    erosion: ErosionConfig
    lakes: LakeConfig
    cleanup: CleanupConfig
    renderer: RendererConfig

    @classmethod
    def from_toml(cls, path: str | Path) -> Config:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            world=WorldConfig(**data.get("world", {})),
            voronoi=VoronoiConfig(**data.get("voronoi", {})),
            sea=SeaConfig(**data.get("sea", {})),
            lakes=LakeConfig(**data.get("lakes", {})),
            erosion=ErosionConfig(**data.get("erosion", {})),
            cleanup=CleanupConfig(**data.get("cleanup", {})),
            renderer=RendererConfig(**data.get("renderer", {})),
        )


@func_timer
def load_config(path: str | Path) -> Config:
    if isinstance(path, str):
        path = Path(path)

    return Config.from_toml(path)

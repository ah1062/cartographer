from __future__ import annotations

from noise import pnoise2

from cartographer.config import Config
from cartographer.models.enums import RegionType
from cartographer.models.world import World


class ElevationPass:
    name = "elevation"

    def __init__(
        self,
        *,
        scale: float = 500.0,
        octaves: int = 6,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        sea_level: float = 0.42,
        mountain_level: float = 0.78,
        seed: int = 42,
    ):
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        self.sea_level = sea_level
        self.mountain_level = mountain_level

        self.seed = seed

    def apply(self, world: World, config: Config, rng):
        elevation = self._generate_elevation(world, config)
        self._apply_falloff(world, config, elevation)

        values = sorted(elevation.values())

        deepsea_ratio = 0.20
        deepsea_cutoff = values[int(len(values) * deepsea_ratio)]

        sea_ratio = 0.42
        sea_cutoff = values[int(len(values) * sea_ratio)]

        for node, value in elevation.items():
            if value < deepsea_cutoff:
                region_type = RegionType.DEEPSEA
            elif value < sea_cutoff:
                region_type = RegionType.SEA
            else:
                region_type = RegionType.LAND

            world.regions[node].region_type = region_type
            world.regions[node].elevation = value
            world.graph.nodes[node]["region_type"] = region_type
            world.graph.nodes[node]["elevation"] = value

    def _generate_elevation(
        self,
        world,
        config,
    ):
        elevation = {}

        G = world.graph
        regions = world.regions
        for node in G.nodes:
            region = regions[node]
            centroid = region.geometry.centroid

            x = centroid.x
            y = centroid.y

            value = pnoise2(
                x,
                y,
                octaves=self.octaves,
                persistence=0.5,
                lacunarity=2.0,
                repeatx=999999,
                repeaty=999999,
                base=config.world.seed,
            )

            elevation[node] = value

        return elevation

    def _apply_falloff(self, world, config, elevation: dict[int, float]):
        for node in elevation:
            centroid = world.regions[node].geometry.centroid

            x = centroid.x / config.world.width
            y = centroid.y / config.world.height

            dx = x - 0.5
            dy = y - 0.5

            dist = (dx * dx + dy * dy) ** 0.5
            elevation[node] -= dist * 1.25

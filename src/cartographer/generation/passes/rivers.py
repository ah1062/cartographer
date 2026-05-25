from __future__ import annotations

import numpy as np

from cartographer.models.enums import RegionFlags, RegionType


class RiverGenerationPass:
    name = "rivers"

    def __init__(
        self,
        *,
        river_count: int = 12,
        min_length: int = 6,
        elevation_key: str = "elevation",
        source_percentile: float = 0.9,
    ):
        self.river_count = river_count
        self.min_length = min_length
        self.elevation_key = elevation_key
        self.source_percentile = source_percentile

    def apply(self, world, config, rng: np.random.Generator):
        land_nodes = [
            n for n, d in world.graph.nodes(data=True)
            if world.regions[n].region_type == RegionType.LAND
        ]

        if not land_nodes:
            world.rivers = []
            return

        elevations = np.array([
            world.regions[n].elevation
            for n in land_nodes
        ])

        threshold = np.percentile(elevations, self.source_percentile)

        sources = [
            n for n in land_nodes
            if getattr(world.regions[n], self.elevation_key, 0.0) >= threshold
        ]

        if not sources:
            world.rivers = []
            return

        rng.shuffle(sources)

        rivers = []
        used = set()
        for s in sources:
            if len(rivers) >= self.river_count:
                break

            if s in used:
                continue

            path = self._trace_river(world, s, used)

            if len(path) >= self.min_length:
                rivers.append(path)
                used.update(path)

        world.rivers = rivers

    def _trace_river(self, world, start, used):
        path = [start]
        current = start

        visited = set()

        while True:
            if len(path) > 500:
                break

            visited.add(current)

            next_node = self._downhill_neighbor(world, current)
            if next_node is None:
                break

            if next_node in visited:
                break

            path.append(next_node)
            region = world.regions[next_node]

            # stop at water bodies
            if region.region_type in (RegionType.SEA, RegionType.DEEPSEA) or region.region_flags & RegionFlags.LAKE:
                break

            current = next_node

        return path

    def _downhill_neighbor(self, world, node):
        neighbors = list(world.graph.neighbors(node))
        if not neighbors:
            return None

        def elev(n):
            return getattr(world.regions[n], self.elevation_key, 0.0)

        current_elev = elev(node)

        lower = [n for n in neighbors if elev(n) < current_elev]

        # prefer true downhill moves
        if lower:
            return min(lower, key=elev)

        # fallback: small random descent step to escape plateaus
        return min(neighbors, key=elev)

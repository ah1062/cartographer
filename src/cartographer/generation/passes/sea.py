from __future__ import annotations

import logging
from collections import deque

from shapely.geometry import box

from cartographer.models.enums import RegionType

logger = logging.getLogger(__name__)


class SeaPass:
    def apply(self, world, config, rng):
        bbox = box(0, 0, config.world.width, config.world.height)
        edge = self._detect_edge_regions(world, bbox)
        sea = set(edge)
        logger.info(f"Found {len(sea)} regions on the edge of the board")

        target = max(
            len(edge) + 1,
            int(len(world.regions) * config.sea.sea_ratio),
        )

        frontier = deque(edge)
        while frontier and len(sea) < target:
            current = frontier.pop()
            candidates = [n for n in world.graph.neighbors(current) if n not in sea]

            if not candidates:
                continue

            nxt = int(rng.choice(candidates))

            sea.add(nxt)
            frontier.append(nxt)

        logger.info(f"Setting {len(sea)} regions to be sea territories")
        for i in sea:
            world.regions[i].region_type = RegionType.SEA
            world.graph.nodes[i]["region_type"] = RegionType.SEA

        for i in sea:
            region = world.regions[i]
            if region.region_type != RegionType.SEA:
                continue

            neighbors = list(world.graph.neighbors(i))
            if not neighbors:
                continue

            if all(
                world.regions[n].region_type in [RegionType.SEA, RegionType.DEEPSEA]
                for n in neighbors
            ):
                region.region_type = RegionType.DEEPSEA
                world.graph.nodes[i]["region_type"] = RegionType.DEEPSEA

    def _detect_edge_regions(self, world, bbox):
        minx, miny, maxx, maxy = bbox.bounds

        edge = set()
        for region in world.regions.values():
            x, y = region.geometry.exterior.coords.xy
            if (
                min(x) <= minx + 1e-5
                or max(x) >= maxx - 1e-5
                or min(y) <= miny + 1e-5
                or max(y) >= maxy - 1e-5
            ):
                edge.add(region.id)

        return edge

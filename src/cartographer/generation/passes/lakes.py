from __future__ import annotations

from collections import deque

import networkx as nx

from cartographer.models.enums import RegionFlags, RegionType


class GenerationLakePass:
    name = "lakes"

    # =========================================================
    # ENTRY
    # =========================================================

    def apply(self, world, config, rng):
        inland = self._find_inland_land(world, config)
        if not inland:
            return

        lake_count = max(
            1,
            rng.poisson(config.lakes.poisson_mean),
        )

        lake_count = min(lake_count, len(inland))

        seeds = rng.choice(
            inland,
            size=lake_count,
            replace=False,
        )

        for seed in seeds:
            self._grow_lake(world, config, rng, int(seed))

    # =========================================================
    # INLAND DETECTION
    # =========================================================

    def _find_inland_land(self, world, config):
        sea_nodes = [
            n
            for n, r in world.regions.items()
            if r.region_type
            in (
                RegionType.SEA,
                RegionType.DEEPSEA,
            )
        ]

        if not sea_nodes:
            return []

        distances = nx.multi_source_dijkstra_path_length(
            world.graph,
            sea_nodes,
        )

        inland = []
        for node, region in world.regions.items():
            if region.region_type != RegionType.LAND:
                continue

            d = distances.get(node, 0)
            if d >= config.lakes.min_inland_distance:
                inland.append(node)

        return inland

    # =========================================================
    # LAKE GROWTH
    # =========================================================

    def _grow_lake(self, world, config, rng, seed: int):
        target_size = min(
            config.lakes.max_size,
            max(
                1,
                rng.poisson(config.lakes.average_size),
            ),
        )

        visited = {seed}
        frontier = deque([seed])

        lake_nodes = []
        while frontier and len(lake_nodes) < target_size:
            current = frontier.popleft()

            region = world.regions[current]

            if region.region_type != RegionType.LAND:
                continue

            # convert to lake
            region.region_type = RegionType.SEA
            world.graph.nodes[current]["region_type"] = RegionType.SEA

            region.region_flags |= RegionFlags.LAKE
            world.graph.nodes[current]["region_flags"] = region.region_flags

            lake_nodes.append(current)

            neighbors = list(world.graph.neighbors(current))
            rng.shuffle(neighbors)

            for nb in neighbors:
                if nb in visited:
                    continue

                visited.add(nb)
                nb_region = world.regions[nb]
                if nb_region.region_type != RegionType.LAND:
                    continue

                # stochastic growth
                if rng.random() < 0.65:
                    frontier.append(nb)

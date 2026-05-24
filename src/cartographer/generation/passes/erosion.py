from __future__ import annotations

import math

import networkx as nx

from cartographer.models.enums import RegionType


class ErosionPass:
    name = "erosion"

    # =========================================================
    # ENTRY
    # =========================================================

    def apply(self, world, config, rng):
        if not config.erosion.enabled:
            return

        for _ in range(config.erosion.iterations):
            self._erode(world, config, rng)

    # =========================================================
    # MAIN EROSION STEP
    # =========================================================

    def _erode(self, world, config, rng):
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
            return

        # shortest graph distance to any sea node
        distances = nx.multi_source_dijkstra_path_length(
            world.graph,
            sea_nodes,
        )

        to_sea = []

        for node, region in world.regions.items():
            if region.region_type != RegionType.LAND:
                continue

            d = distances.get(node)

            if d is None:
                continue

            # preserve stable continental interiors
            if d >= config.erosion.preserve_core_distance:
                continue

            # exponential coastal decay
            pressure = math.exp(-d / config.erosion.falloff)

            # probabilistic erosion
            probability = pressure * config.erosion.erosion_strength

            # slight coastal noise variation
            probability *= rng.uniform(0.85, 1.15)

            if rng.random() < probability:
                to_sea.append(node)

        # apply simultaneously
        for node in to_sea:
            region = world.regions[node]

            region.region_type = RegionType.SEA
            world.graph.nodes[node]["region_type"] = RegionType.SEA

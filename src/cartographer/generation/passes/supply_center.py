from __future__ import annotations

import networkx as nx
import numpy as np

from cartographer.models.enums import RegionType


class SupplyCenterPass:
    name = "supply_centers"

    def __init__(
        self,
        *,
        ratio: float = 0.25,
        min_distance: int = 8,
        mainland_bias: float = 0.2,
    ):
        self.ratio = ratio
        self.min_distance = min_distance
        self.mainland_bias = mainland_bias

    # =========================================================
    # ENTRY
    # =========================================================

    def apply(self, world, config, rng: np.random.Generator):
        land_nodes = [
            n for n, d in world.graph.nodes(data=True)
            if d.get("region_type") == RegionType.LAND
        ]

        if not land_nodes:
            return

        land_sub = world.graph.subgraph(land_nodes)
        components = list(nx.connected_components(land_sub))

        sc_count = max(10, int(len(land_nodes) * self.ratio))

        # 1. guarantee 1 SC per island/continent
        chosen = set()
        remaining_budget = sc_count

        components = sorted(components, key=len, reverse=True)

        for comp in components:
            if remaining_budget <= 0:
                break

            node = self._pick_random_node(comp, rng)
            chosen.add(node)
            remaining_budget -= 1

        # 2. assign remaining SCs to mainland (largest comp)
        if components and remaining_budget > 0:
            mainland = components[0]
            mainland_nodes = list(mainland)

            for _ in range(remaining_budget):
                node = self._pick_random_node(mainland_nodes, rng)
                chosen.add(node)

        # 3. apply
        for n in chosen:
            world.regions[n].supply_center = True

    # =========================================================
    # RANDOM PICK
    # =========================================================

    def _pick_random_node(self, nodes, rng):
        return list(nodes)[int(rng.integers(0, len(nodes)))]

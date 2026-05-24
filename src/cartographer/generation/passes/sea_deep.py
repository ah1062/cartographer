# cartographer/generation/passes/deepsea.py

from __future__ import annotations

import networkx as nx

from cartographer.models.enums import RegionType
from cartographer.utils.timing import func_timer


class DeepSeaPass:
    def apply(self, world, config, rng):
        self._deepen_seas(world)
        self._reduce_small_deepsea_clusters(world, config)

    @func_timer
    def _deepen_seas(self, world):
        G = world.graph
        for node, data in G.nodes(data=True):
            if data["region_type"] != RegionType.SEA:
                continue

            neighbours = list(G.neighbors(node))
            if not neighbours:
                continue

            surrounded = all(
                G.nodes[n]["region_type"] in [RegionType.SEA, RegionType.DEEPSEA]
                for n in neighbours
            )
            if surrounded:
                world.regions[node].region_type = RegionType.DEEPSEA
                G.nodes[node]["region_type"] = RegionType.DEEPSEA

    @func_timer
    def _reduce_small_deepsea_clusters(self, world, config):
        G = world.graph

        nodes = [n for n, d in G.nodes(data=True) if d["region_type"] == RegionType.DEEPSEA]

        subgraph = G.subgraph(nodes)
        for component in nx.connected_components(subgraph):
            if len(component) >= config.sea.deepsea_minimum_size:
                continue

            for node in component:
                world.regions[node].region_type = RegionType.SEA
                G.nodes[node]["region_type"] = RegionType.SEA

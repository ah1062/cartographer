from __future__ import annotations

import networkx as nx
import numpy as np

from cartographer.models.enums import RegionType


class SupplyCenterPass:
    name = "supply_centers"

    def __init__(
        self,
        *,
        ratio: float = 0.03,
        min_distance: int = 3,
        mainland_bias: float = 0.5,
        degree_weight: float = 0.6,
        betweenness_weight: float = 0.4,
        coastal_penalty: float = 0.85,
    ):
        self.ratio = ratio
        self.min_distance = min_distance
        self.mainland_bias = mainland_bias

        self.degree_weight = degree_weight
        self.betweenness_weight = betweenness_weight
        self.coastal_penalty = coastal_penalty

    def apply(self, world, config, rng: np.random.Generator):
        land_nodes = [
            n for n, d in world.graph.nodes(data=True) if d.get("region_type") == RegionType.LAND
        ]

        if not land_nodes:
            return

        land_sub = world.graph.subgraph(land_nodes)
        continents = list(nx.connected_components(land_sub))

        sc_count = max(10, int(len(land_nodes) * self.ratio))

        allocations = self._allocate(sc_count, continents, rng)
        self._bias_mainland(allocations, continents, sc_count, rng)

        selected = set()

        for comp, k in zip(continents, allocations):
            chosen = self._select_for_component(world, comp, k, rng)
            selected.update(chosen)

        for n in selected:
            world.regions[n].supply_center = True

    def _allocate(self, sc_count, continents, rng):
        sizes = np.array([len(c) for c in continents], dtype=float)
        total = sizes.sum()

        raw = sc_count * sizes / total
        alloc = np.maximum(1, raw.astype(int))

        # stochastic rounding cleanup (uses rng now)
        while alloc.sum() > sc_count:
            i = rng.integers(0, len(alloc))
            if alloc[i] > 1:
                alloc[i] -= 1

        return alloc.tolist()

    def _bias_mainland(self, alloc, continents, sc_count, rng):
        if not continents:
            return

        mainland_idx = int(np.argmax([len(c) for c in continents]))
        desired = int(sc_count * self.mainland_bias)

        diff = desired - alloc[mainland_idx]
        if diff <= 0:
            return

        alloc[mainland_idx] += diff

        i = 0
        while diff > 0:
            if i == mainland_idx:
                i = (i + 1) % len(alloc)
                continue

            if alloc[i] > 1:
                alloc[i] -= 1
                diff -= 1

            i = (i + 1) % len(alloc)

    def _select_for_component(self, world, comp, k, rng):
        sub = world.graph.subgraph(comp)

        degree = nx.degree_centrality(sub)
        between = nx.betweenness_centrality(sub, normalized=True)

        def score(n):
            base = self.degree_weight * degree.get(n, 0.0) + self.betweenness_weight * between.get(
                n, 0.0
            )

            if "coast" in world.regions[n].metadata.get("tags", []):
                base *= self.coastal_penalty

            return base

        ordered = sorted(comp, key=score, reverse=True)

        chosen = []
        for node in ordered:
            if len(chosen) >= k:
                break

            if self._is_valid(world, node, chosen):
                chosen.append(node)

        return chosen

    def _is_valid(self, world, node, chosen):
        if not chosen:
            return True

        for c in chosen:
            try:
                dist = nx.shortest_path_length(world.graph, node, c)
            except nx.NetworkXNoPath:
                continue

            if dist < self.min_distance:
                return False

        return True

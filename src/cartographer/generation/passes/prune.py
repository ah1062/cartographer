from __future__ import annotations

import logging

import networkx as nx
from shapely.validation import make_valid

from cartographer.config import Config
from cartographer.models import World
from cartographer.models.enums import RegionFlags, RegionType
from cartographer.utils import func_timer

logger = logging.getLogger(__name__)


class PruningPass:
    name = "cleanup"

    def apply(self, world: World, config: Config, rng):
        self._prune_small_regions(world, config)
        self._prune_single_seas(world, config)
        self._define_after_lakes(world, config)

    @func_timer
    def _prune_small_regions(self, world: World, config: Config):
        min_area = config.cleanup.min_area_fraction * (config.world.width * config.world.height)
        to_remove = [
            rid
            for rid, r in world.regions.items()
            if r.geometry is None or r.geometry.area < min_area
        ]

        logger.info("Pruning %d small regions", len(to_remove))
        for rid in to_remove:
            if rid not in world.regions:
                continue

            region = world.regions[rid]
            neighbors = list(world.graph.neighbors(rid)) if world.graph.has_node(rid) else []

            # safe removal if isolated
            if not neighbors:
                world.graph.remove_node(rid)
                del world.regions[rid]
                continue

            # merge into largest neighbor (stable heuristic)
            target = max(
                neighbors,
                key=lambda n: world.regions[n].geometry.area if world.regions[n].geometry else 0,
            )

            target_region = world.regions[target]

            geom_a = make_valid(target_region.geometry)
            geom_b = make_valid(region.geometry)

            merged = geom_a.union(geom_b)
            target_region.geometry = merged

            # transfer metadata if needed
            target_region.metadata.setdefault("merged", []).append(rid)

            # remove node
            world.graph.remove_node(rid)
            del world.regions[rid]

        # optional: clean graph
        self._repair_graph(world)

    def _repair_graph(self, world: World):
        """
        Ensures no dangling edges or missing nodes after pruning/merging.
        """

        to_remove = [n for n in world.graph.nodes if n not in world.regions]

        for n in to_remove:
            world.graph.remove_node(n)

        # rebuild missing adjacency edges (cheap repair pass)
        for a in world.regions:
            for b in world.graph.neighbors(a):
                if b not in world.regions:
                    continue
                world.graph.add_edge(a, b)

    def _prune_single_seas(self, world: World, config: Config):
        sea_nodes = [i for i, n in world.regions.items() if n.region_type == RegionType.SEA]

        for sea in sea_nodes:
            neighbors = [world.regions[i] for i in world.graph.neighbors(sea)]

            if len(neighbors) == 0:
                continue

            if all(map(lambda r: r.region_type == RegionType.LAND, neighbors)):
                world.regions[sea].region_type = RegionType.LAND
                world.graph.nodes[sea]["region_type"] = RegionType.LAND

    def _define_after_lakes(self, world: World, config: Config):
        # 1. collect sea nodes
        sea_nodes = [
            n
            for n, d in world.graph.nodes(data=True)
            if d.get("region_type") in (RegionType.SEA, RegionType.DEEPSEA)
        ]

        sea_subgraph = world.graph.subgraph(sea_nodes)

        inland_seas = []
        ocean_seas = []

        # 2. connected components of sea
        for comp in nx.connected_components(sea_subgraph):
            comp_set = set(comp)

            is_inland = True

            for node in comp_set:
                for nb in world.graph.neighbors(node):
                    # if it touches ANY sea outside this component → ocean-connected
                    if nb not in comp_set and world.regions[nb].region_type in (
                        RegionType.SEA,
                        RegionType.DEEPSEA,
                    ):
                        is_inland = False
                        break

                if not is_inland:
                    break

            if is_inland:
                inland_seas.append(comp_set)
            else:
                ocean_seas.append(comp_set)

        for sea in inland_seas:
            for sid in sea:
                region = world.regions[sid]
                region.region_flags |= RegionFlags.LAKE
                world.graph.nodes[sid]["region_flags"] = region.region_flags

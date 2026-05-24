from __future__ import annotations

import logging

from shapely.strtree import STRtree

from cartographer.utils import func_timer

logger = logging.getLogger(__name__)


class GraphPass:
    def apply(self, world, config, rng):
        count = self._build_nodes(world)
        logger.info(f"Created graph nodes for {count} regions")

        if world.voronoi:
            count = self._build_voronoi_edges(world)
        else:
            count = self._build_geometry_edges(world)
        logger.info(f"Created {count} graph adjacencies between regions")

    @func_timer
    def _build_nodes(self, world):
        G = world.graph

        count = 0
        for region in world.regions.values():
            G.add_node(
                region.id,
                region=region,
                region_type=region.region_type,
                tags=[],
            )
            count += 1

        return count

    @func_timer
    def _build_voronoi_edges(self, world):
        G = world.graph

        count = 0
        for a, b in world.voronoi.ridge_points:
            if a not in world.regions:
                continue

            if b not in world.regions:
                continue

            count += 1
            G.add_edge(a, b)
        return count

    @func_timer
    def build_geometry_edges(self, world):
        G = world.graph
        regions = world.regions

        G.clear()

        ids = list(regions.keys())
        geoms = [regions[i].geometry for i in ids]

        tree = STRtree(geoms)
        geom_to_id = {id(geom): rid for rid, geom in zip(ids, geoms)}

        count = 0
        for rid, geom in zip(ids, geoms):
            G.add_node(rid)

            for candidate in tree.query(geom):
                cid = geom_to_id[id(candidate)]

                if cid == rid:
                    continue

                if geom.touches(candidate):
                    count += 1
                    G.add_edge(rid, cid)

        return count

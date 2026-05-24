import logging

import networkx as nx
from shapely.ops import unary_union

from cartographer.models.enums import RegionFlags

logger = logging.getLogger(__name__)


class RenderLakePass:
    name = "lakes"

    def __init__(self, renderer):
        self.r = renderer

    def render(self, draw, world):
        lake_nodes = [n for n, r in world.regions.items() if RegionFlags.LAKE in r.region_flags]

        sub = world.graph.subgraph(lake_nodes)

        lakes = list(nx.connected_components(sub))
        logger.info(f"Identified {len(lakes)} lakes to outline")
        for comp in lakes:
            self._draw_lake(draw, world, comp)

    def _draw_lake(self, draw, world, nodes):
        polys = [world.regions[n].geometry for n in nodes]
        merged = unary_union(polys)

        if merged.is_empty:
            return

        draw.line(
            merged.exterior.coords,
            fill=self.r.edge_colour,
            width=self.r.edge_width * 5,
        )

import networkx as nx
from shapely.ops import unary_union

from cartographer.models.enums import RegionType


class ContinentPass:
    name = "continents"

    def __init__(self, renderer):
        self.r = renderer

    def render(self, draw, world):
        land_nodes = [
            n for n, d in world.graph.nodes(data=True) if d.get("region_type") == RegionType.LAND
        ]

        sub = world.graph.subgraph(land_nodes)

        for comp in nx.connected_components(sub):
            self._draw_continent(draw, world, comp)

    def _draw_continent(self, draw, world, nodes):
        polys = [world.regions[n].geometry for n in nodes]
        merged = unary_union(polys)

        if merged.is_empty:
            return

        draw.line(
            merged.exterior.coords,
            fill=self.r.edge_colour,
            width=self.r.edge_width * 8,
        )

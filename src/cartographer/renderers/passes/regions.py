from shapely.geometry import MultiPolygon, Polygon


class RegionPass:
    name = "regions"

    def __init__(self, renderer):
        self.r = renderer

    def render(self, draw, world):
        for region in world.regions.values():
            if region.geometry is None:
                continue

            self._draw_geom(draw, region.geometry, region.colour)

    def _draw_geom(self, draw, geom, fill_colour):
        if isinstance(geom, Polygon):
            coords = list(geom.exterior.coords)
            draw.polygon(coords, fill=fill_colour)
            draw.line(coords, fill=self.r.edge_colour, width=self.r.edge_width)

        elif isinstance(geom, MultiPolygon):
            for g in geom.geoms:
                self._draw_geom(draw, g, fill_colour)

class SupplyCenterRenderPass:
    name = "supply_centers"

    def __init__(self, renderer, *, radius: int = 6, fill=(255, 0, 0), outline=(0, 0, 0)):
        self.r = renderer
        self.radius = radius
        self.fill = fill
        self.outline = outline

    def render(self, draw, world):
        for region in world.regions.values():
            if not getattr(region, "supply_center", False):
                continue

            geom = region.geometry
            if geom is None:
                continue

            cx = float(geom.centroid.x)
            cy = float(geom.centroid.y)

            self._draw_circle(draw, cx, cy)

    def _draw_circle(self, draw, cx, cy):
        r = self.radius

        bbox = [
            (cx - r, cy - r),
            (cx + r, cy + r),
        ]

        draw.ellipse(
            bbox,
            fill=self.fill,
            outline=self.outline,
        )

from PIL import ImageFont


class RegionTitlesPass:
    name = "region_titles"

    def __init__(
        self,
        renderer,
        *,
        font_path: str | None = None,
        font_size: int = 12,
        fill=(0, 0, 0),
    ):
        self.r = renderer
        self.font_path = font_path
        self.font_size = font_size
        self.fill = fill

        self.font = self._load_font()

    def render(self, draw, world):
        for region in world.regions.values():
            geom = region.geometry
            if geom is None:
                continue

            x, y = self._get_position(region)

            draw.text(
                (x, y),
                region.name,
                font=self.font,
                fill=self.fill,
                anchor="mm",  # center alignment
            )

    def _get_position(self, region):
        if hasattr(region, "title_coords") and region.title_coords:
            return region.title_coords

        c = region.geometry.centroid
        return (c.x, c.y)

    def _load_font(self):
        try:
            if self.font_path:
                return ImageFont.truetype(self.font_path, self.font_size)

            # common fallback paths
            return ImageFont.truetype("DejaVuSans.ttf", self.font_size)

        except OSError:
            return ImageFont.load_default()

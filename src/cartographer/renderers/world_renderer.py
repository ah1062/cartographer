from __future__ import annotations

import logging
import time

from PIL import Image, ImageDraw, ImageOps

from cartographer.models import World
from cartographer.renderers.passes.factory import RenderPassFactory
from cartographer.utils.timing import func_timer

logger = logging.getLogger(__name__)


class WorldRenderer:
    def __init__(
        self,
        width: int,
        height: int,
        passes: list[str] | None = None,
        *,
        background=(255, 255, 255),
        edge_colour=(0, 0, 0),
        edge_width=1,
    ):
        self.width = width
        self.height = height

        self.background = background
        self.edge_colour = edge_colour
        self.edge_width = edge_width

        if passes is None:
            passes = []
        self._passes = passes

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------

    @func_timer
    def render(self, world: World) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), self.background)
        draw = ImageDraw.Draw(image)

        for p in self._passes:
            stager = RenderPassFactory.create(p, renderer=self)
            start = time.perf_counter()
            stager.render(draw, world)
            
            logger.info(f"Render stage {p} took {time.perf_counter() - start:.3f}")

        return ImageOps.expand(image, border=30, fill=(105, 70, 30))

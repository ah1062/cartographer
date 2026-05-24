from __future__ import annotations

from typing import Protocol

from PIL import ImageDraw

from cartographer.models import World


class RenderPass(Protocol):
    name: str

    def render(self, draw: ImageDraw.ImageDraw, world: World) -> None: ...

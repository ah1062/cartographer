import numpy as np

from cartographer.config import WorldConfig
from cartographer.generation.passes.base import GenerationPass
from cartographer.models import World


class WorldGenerator:
    def __init__(self, config: WorldConfig, passes: list[GenerationPass] | None = None) -> None:
        if passes is None:
            passes = []

        self.config = config
        self.passes = passes

        self.rng = np.random.default_rng(config.seed)
        
    def generate(self) -> World:
        world = World()

        for stage in self.passes:
            stage.apply(world, self.config, self.rng)

        return world

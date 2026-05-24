import numpy as np

from cartographer.config import Config
from cartographer.generation.passes.factory import GenerationPassFactory
from cartographer.models import World


class WorldGenerator:
    def __init__(self, config: Config, passes: list[str] | None = None) -> None:
        if passes is None:
            passes = []

        self.config = config
        self.passes = passes

        self.rng = np.random.default_rng(config.world.seed)

    def generate(self) -> World:
        world = World()

        for stage in self.passes:
            stager = GenerationPassFactory.create(stage)
            stager.apply(world, self.config, self.rng)

        return world

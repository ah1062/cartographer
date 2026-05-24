from __future__ import annotations

from typing import Protocol

import numpy as np

from cartographer.models import World


class GenerationPass(Protocol):
    def apply(
        self,
        world: World,
        config,
        rng: np.random.Generator,
    ) -> None:
        ...

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import numpy as np
from scipy.spatial import Voronoi

from cartographer.models.region import Region
from cartographer.models.unit import Unit


@dataclass
class World:
    points: np.ndarray | None = None
    voronoi: Voronoi | None = None

    regions: dict[int, Region] = field(default_factory=dict)
    graph: nx.Graph = field(default_factory=nx.Graph)
    units: dict[int, Unit] = field(default_factory=dict)

# cartographer/generation/passes/voronoi.py

from __future__ import annotations

import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box

from cartographer.config import Config
from cartographer.models import Region
from cartographer.models.enums import RegionType
from cartographer.models.world import World
from cartographer.utils import func_timer


class VoronoiPass:
    @func_timer
    def apply(self, world: World, config: Config, rng):
        bounds = box(
            0,
            0,
            config.world.width,
            config.world.height,
        )

        points = self._generate_points(config, rng)
        points = self._lloyd_relaxation(config, points)
        vor = Voronoi(points)

        world.points = points
        world.voronoi = vor

        for i, region_idx in enumerate(vor.point_region):
            verts = vor.regions[region_idx]

            if -1 in verts or len(verts) == 0:
                continue

            poly = Polygon(vor.vertices[verts]).intersection(bounds)
            if poly.is_empty:
                continue

            region = Region(
                id=i,
                name=f"r{hex(i)[2:]}",
                geometry=poly,
                region_type=RegionType.LAND,
            )

            world.regions[i] = region

    @func_timer
    def _generate_points(self, config, rng):
        return rng.random((config.world.point_count, 2)) * [
            config.world.width,
            config.world.height,
        ]

    @func_timer
    def _lloyd_relaxation(self, config, points):
        for _ in range(config.voronoi.relaxation_iterations):
            vor = Voronoi(points)

            relaxed = []
            for i, region_idx in enumerate(vor.point_region):
                verts = vor.regions[region_idx]
                if -1 in verts or len(verts) == 0:
                    relaxed.append(points[i])
                    continue

                poly = Polygon(vor.vertices[verts])
                if not poly.is_valid or poly.area == 0:
                    relaxed.append(points[i])
                    continue

                c = poly.centroid
                relaxed.append([c.x, c.y])

            points = np.asarray(relaxed)

        return points

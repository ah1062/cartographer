from cartographer.generation.passes.base import GenerationPass
from cartographer.generation.passes.elevation import ElevationPass
from cartographer.generation.passes.erosion import ErosionPass
from cartographer.generation.passes.graph import GraphPass
from cartographer.generation.passes.lakes import GenerationLakePass
from cartographer.generation.passes.prune import PruningPass
from cartographer.generation.passes.sea import SeaPass
from cartographer.generation.passes.sea_deep import DeepSeaPass
from cartographer.generation.passes.supply_center import SupplyCenterPass
from cartographer.generation.passes.voronoi import VoronoiPass
from cartographer.utils.factory import Factory


class GenerationPassFactory(Factory[GenerationPass]):
    pass


GenerationPassFactory.register("voronoi", VoronoiPass)
GenerationPassFactory.register("elevation", ElevationPass)
GenerationPassFactory.register("graph", GraphPass)
GenerationPassFactory.register("sea", SeaPass)
GenerationPassFactory.register("lakes", GenerationLakePass)
GenerationPassFactory.register("erosion", ErosionPass)
GenerationPassFactory.register("deepsea", DeepSeaPass)
GenerationPassFactory.register("prune", PruningPass)
GenerationPassFactory.register("supply_center", SupplyCenterPass)

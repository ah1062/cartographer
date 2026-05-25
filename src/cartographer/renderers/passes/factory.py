from cartographer.renderers.passes.base import RenderPass
from cartographer.renderers.passes.continents import ContinentPass
from cartographer.renderers.passes.lakes import RenderLakePass
from cartographer.renderers.passes.regions import RegionPass
from cartographer.renderers.passes.supply_center import SupplyCenterRenderPass
from cartographer.renderers.passes.titles import RegionTitlesPass
from cartographer.utils.factory import Factory


class RenderPassFactory(Factory[RenderPass]):
    pass


RenderPassFactory.register("regions", RegionPass)
RenderPassFactory.register("continents", ContinentPass)
RenderPassFactory.register("lakes", RenderLakePass)
RenderPassFactory.register("supply_center", SupplyCenterRenderPass)
RenderPassFactory.register("titles", RegionTitlesPass)

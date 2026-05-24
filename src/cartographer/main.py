from cartographer.config import load_config
from cartographer.constants import CONFIGS_PATH, MAPS_PATH
from cartographer.generation.world_generation import WorldGenerator
from cartographer.renderers.world_renderer import WorldRenderer
from cartographer.utils.logging import setup_logging


def main():
    config_path = CONFIGS_PATH / "default.toml"
    cfg = load_config(config_path)
    generator = WorldGenerator(
        cfg,
        passes=[
            "voronoi",
            "graph",
            "elevation",
            "sea",
            "erosion",
            "erosion",
            "erosion",
            "lakes",
            "deepsea",
            "prune",
            "supply_center",
        ],
    )

    renderer = WorldRenderer(
        cfg.world.width,
        cfg.world.height,
        passes=["regions", "continents", "lakes", "supply_center"],
    )

    world = generator.generate()
    image = renderer.render(world)

    name = f"map{cfg.world.seed}.png"
    image.save(MAPS_PATH / name, format="png")


def cli():
    setup_logging()
    main()


if __name__ == "__main__":
    setup_logging()
    main()

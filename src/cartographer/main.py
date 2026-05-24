from cartographer.config import load_config
from cartographer.generation.world_generation import WorldGenerator
from cartographer.utils.logging import setup_logging


def main():
    print("Hello from cartographer!")

    config = load_config("config.toml")
    generator = WorldGenerator(
        config
    )


def cli():
    setup_logging()
    main()

if __name__ == "__main__":
    setup_logging()
    main()

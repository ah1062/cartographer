import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorldConfig:
    width: int
    height: int
    seed: int

def load_config(path: str | Path) -> WorldConfig:
    if isinstance(path, str):
        path = Path(path)

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    w = raw.get("world", {})

    return WorldConfig(
        width=w.get("width", 10000),
        height=w.get("height", 10000),
        seed=w.get("seed", 42)
    )

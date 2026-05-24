from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")


class Factory(ABC, Generic[T]):
    REGISTRY: dict[str, type[T]] = {}

    def __init_subclass__(cls) -> None:
        cls.REGISTRY = {}

    @classmethod
    def register(cls, method, obj: type[T]):
        cls.REGISTRY[method] = obj

    @classmethod
    def create(cls, method, *args, **kwargs) -> T:
        if method not in cls.REGISTRY:
            methods = "\n".join(f"- {k}" for k in cls.REGISTRY.keys())
            raise ValueError(
                f"Can't provide supplied method: '{method}'\nAvailable methods:\n{methods}"
            )

        return cls.REGISTRY[method](*args, **kwargs)

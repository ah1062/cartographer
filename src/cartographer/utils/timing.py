import logging
import time

logger = logging.getLogger(__name__)


def func_timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        logger.info(f"{func.__name__} took {end - start:.4f}s")
        return result

    return wrapper

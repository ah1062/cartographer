import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y/%m/%d %H:%M:%S",
        format="[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    )

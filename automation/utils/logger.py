import logging
import sys


def setup(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("sop")
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


log = setup()

import logging


def make_logger(name: str, fmt: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(fmt))
    logger.addHandler(h)
    return logger

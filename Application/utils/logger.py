"""
ScamShield — App-wide Logger
"""
import logging
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scamshield.log")


def get_logger(name: str = "scamshield") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger


import logging
import sys

logger = logging.getLogger("deltav")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(msg)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

def info(*args, **kwargs):
    logger.info(*args, **kwargs)

def warn(*args, **kwargs):
    logger.warn(*args, **kwargs)

def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)
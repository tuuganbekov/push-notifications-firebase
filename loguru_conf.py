# logging.py
import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "debug.log"

logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add(
    LOG_FILE,
    level="ERROR",
    rotation="100 KB",
    compression="zip",
    retention="1 minute",
)

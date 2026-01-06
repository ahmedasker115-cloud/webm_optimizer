import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bn_optimizer.log"

def setup_logging():
    logger = logging.getLogger("bn_optimizer")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fmt = logging.Formatter('{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","msg":"%(message)s"}')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    # also keep a simple console handler for developer runs
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)
    return logger


# convenience
logger = setup_logging()

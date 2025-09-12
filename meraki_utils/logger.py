import logging
import sys

def setup_logger(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    sys.stdout.flush()

setup_logger(debug=True)
logger = logging.getLogger("meraki-automation")

_log_callback = None

def set_log_callback(callback):
    global _log_callback
    _log_callback = callback

def log(msg, level="info"):
    if _log_callback:
        _log_callback(msg)
    getattr(logger, level)(msg)

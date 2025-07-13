import logging
from ..interfaces.Ilogger import LoggerInterface

_loggers = {}

def get_logger(name: str = "taskqueue") -> LoggerInterface:
    """
    Returns a singleton logger instance for the given name.
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        _loggers[name] = logger
    return _loggers[name]

logger = get_logger()
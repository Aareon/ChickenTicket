import logging
import sys
from logging.handlers import RotatingFileHandler

_levels = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def filter_status(record):
    """"
    Only displays log messages about status info
    or ERROR level
    """
    return "Status:" in str(record.msg) or record.levelname == 'ERROR'


def getLogger(logFile, level_input="WARNING", terminal_output=False):
    level = _levels.get(level_input)
    if level is None:
        raise AttributeError('level not recognized')

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(level)
    logger = logging.getLogger('root')
    logger.setLevel(level)
    logger.addHandler(my_handler)

    # This part is what goes on console.
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)

    if not terminal_output:
        formatter = logging.Formatter('%(asctime)s %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if terminal_output:
        logger.debug('Logging level: {} ({})'.format(level_input, level))

    return logger

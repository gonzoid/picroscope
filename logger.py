import logging
import sys

def create_logger(logger_name, log_level='debug', log_file=None):
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    LOG_FORMAT = '%(asctime)s %(name)-13s %(levelname)-8s: %(message)s'
    LOG_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    logger = logging.getLogger(logger_name)
    logger.setLevel(levels[log_level] if log_level in levels else 'debug')

    if not log_file:
        stdout = logging.StreamHandler(sys.stdout)
    else:
        stdout = logging.FileHandler(log_file)

    stdout.setFormatter(formatter)
    logger.addHandler(stdout)
 
    return logger

"""
Stackify Python API
"""

__version__ = '0.0.1'


API_URL = 'https://api.stackify.com'

READ_TIMEOUT = 5000

MAX_BATCH = 100

QUEUE_SIZE = 1000

import logging
import inspect

DEFAULT_LEVEL = logging.ERROR

LOGGING_LEVELS = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET'
}

logging.basicConfig()

internal_log = logging.getLogger(__name__)


from stackify.application import ApiConfiguration
from stackify.http import HTTPClient

from stackify.handler import StackifyHandler


def getLogger(name=None, **kwargs):
    if not name:
        try:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            name = module.__name__
        except IndexError:
            name = 'stackify-python-unknown'

    logger = logging.getLogger(name)

    if not [isinstance(x, StackifyHandler) for x in logger.handlers]:
        internal_log.debug('Creating handler for logger {0}'.format(name))
        handler = StackifyHandler(**kwargs)
        logger.addHandler(handler)

        if logger.getEffectiveLevel() == logging.NOTSET:
            logger.setLevel(DEFAULT_LEVEL)

    return logger



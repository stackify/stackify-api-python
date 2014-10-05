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


# TODO
# holds our listeners, since more than one handler can service
# the same listener
__listener_cache = {}


def getLogger(name=None, **kwargs):
    '''
    Get a logger and attach a StackifyHandler if needed:w
    '''
    if not name:
        name = getCallerName(2)

    logger = logging.getLogger(name)

    if not [isinstance(x, StackifyHandler) for x in logger.handlers]:
        internal_log.debug('Creating handler for logger {0}'.format(name))
        handler = StackifyHandler(**kwargs)
        logger.addHandler(handler)

        if logger.getEffectiveLevel() == logging.NOTSET:
            logger.setLevel(DEFAULT_LEVEL)

        handler.listener.start()

    return logger

def stopLogging(logger):
    '''
    Shut down the StackifyHandler on a given logger. This will block
    and wait for the queue to finish uploading.
    '''
    for handler in getHandlers(logger):
        handler.listener.stop()


def getCallerName(levels=1):
    '''
    Gets the name of the module calling this function
    '''
    try:
        frame = inspect.stack()[levels]
        module = inspect.getmodule(frame[0])
        name = module.__name__
    except IndexError:
        name = 'stackify-python-unknown'
    return name


def getHandlers(logger):
    '''
    Return the StackifyHandlers on a given logger
    '''
    return [isinstance(x, StackifyHandler) for x in logger.handlers]


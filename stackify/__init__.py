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
import atexit

DEFAULT_LEVEL = logging.ERROR

LOGGING_LEVELS = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET'
}


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger(__name__).addHandler(NullHandler())


from stackify.application import ApiConfiguration
from stackify.http import HTTPClient

from stackify.handler import StackifyHandler


def getLogger(name=None, auto_shutdown=True, basic_config=True, **kwargs):
    '''
    Get a logger and attach a StackifyHandler if needed.
    '''
    if basic_config:
        logging.basicConfig()

    if not name:
        name = getCallerName(2)

    logger = logging.getLogger(name)

    if not [isinstance(x, StackifyHandler) for x in logger.handlers]:
        internal_logger = logging.getLogger(__name__)
        internal_logger.debug('Creating handler for logger %s', name)
        handler = StackifyHandler(**kwargs)
        logger.addHandler(handler)

        if auto_shutdown:
            internal_logger.debug('Registering atexit callback')
            atexit.register(stopLogging, logger)

        if logger.getEffectiveLevel() == logging.NOTSET:
            logger.setLevel(DEFAULT_LEVEL)

        handler.listener.start()

    return logger


def stopLogging(logger):
    '''
    Shut down the StackifyHandler on a given logger. This will block
    and wait for the queue to finish uploading.
    '''
    internal_logger = logging.getLogger(__name__)
    internal_logger.debug('Shutting down all handlers')
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
    return [x for x in logger.handlers if isinstance(x, StackifyHandler)]

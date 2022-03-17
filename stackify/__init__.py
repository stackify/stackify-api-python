"""
Stackify Python API
"""
__version__ = '1.2.0'

import logging
import inspect
import atexit

from stackify.constants import DEFAULT_LEVEL
from stackify.handler import StackifyHandler


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


internal_logger = logging.getLogger(__name__)
internal_logger.addHandler(NullHandler())
internal_logger.propagate = False
internal_logger.setLevel(DEFAULT_LEVEL)


def getLogger(name=None, auto_shutdown=True, basic_config=True, **kwargs):
    '''Get a logger and attach a StackifyHandler if needed.

    You can pass this function keyword arguments for Stackify configuration.
    If they are omitted you can specify them through environment variables:
     * STACKIFY_API_KEY
     * STACKIFY_APPLICATION
     * STACKIFY_ENVIRONMENT
     * STACKIFY_API_URL

    Args:
        name: The name of the logger (or None to automatically make one)
        auto_shutdown: Register an atexit hook to shut down logging
        basic_config: Set up with logging.basicConfig() for regular logging

    Optional Args:
        api_key: Your Stackify API key
        application: The name of your Stackify application
        environment: The Stackfiy environment to log to
        api_url: An optional API url if required

    Returns:
        A logger instance with Stackify handler and listener attached.
    '''
    if basic_config:
        logging.basicConfig()

    if not name:
        name = getCallerName(2)

    logger = logging.getLogger(name)

    if not any([isinstance(x, StackifyHandler) for x in logger.handlers]):
        internal_logger.debug('Creating handler for logger %s', name)

        if auto_shutdown:
            internal_logger.debug('Registering atexit callback')
            atexit.register(stopLogging, logger)

        if logger.getEffectiveLevel() == logging.NOTSET:
            logger.setLevel(DEFAULT_LEVEL)

        handler = StackifyHandler(ensure_at_exit=not auto_shutdown, **kwargs)
        logger.addHandler(handler)

    return logger


def stopLogging(logger):
    '''Stop logging on the Stackify handler.

    Shut down the StackifyHandler on a given logger. This will block
    and wait for the queue to finish uploading.
    '''

    internal_logger.debug('Shutting down all handlers')
    for handler in getHandlers(logger):
        handler.listener.stop()


def getCallerName(levels=1):
    '''Gets the name of the module calling this function'''
    try:
        frame = inspect.stack()[levels]
        module = inspect.getmodule(frame[0])
        name = module.__name__
    except IndexError:
        name = 'stackify-python-unknown'
    return name


def getHandlers(logger):
    '''Return the StackifyHandlers on a given logger'''
    return [x for x in logger.handlers if isinstance(x, StackifyHandler)]

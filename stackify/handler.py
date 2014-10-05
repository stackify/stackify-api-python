import logging
import threading
import os

try:
    from logging.handlers import QueueHandler, QueueListener
except:
    from stackify.handler_backport import QueueHandler, QueueListener

try:
    import Queue as queue
except ImportError:
    import queue

from stackify import QUEUE_SIZE, API_URL
from stackify.log import LogMsg
from stackify.error import ErrorItem
from stackify.http import HTTPClient
from stackify.application import ApiConfiguration



class StackifyHandler(QueueHandler):
    '''
    A handler class to format and queue log messages for later
    transmission to Stackify servers.
    '''

    def __init__(self, queue_=None, listener=None **kwargs):
        if queue_ is None:
            queue_ = queue.Queue(QUEUE_SIZE)

        super(StackifyHandler, self).__init__(queue_)

        if listener is None:
            listener = StackifyListener(queue_, **kwargs)

        self.listener = listener

    def enqueue(self, record):
        '''
        Put a new record on the queue. If it's full, evict an item.
        '''
        try:
            self.queue.put_nowait(record)
            logger = logging.getLogger(__name__)
            logger.debug('put record ' + record.toJSON())
        except queue.Full:
            logger = logging.getLogger(__name__)
            logger.warn('StackifyHandler queue is full, evicting oldest record')
            self.queue.get_nowait()
            self.queue.put_nowait(record)

    def prepare(self, record):
        msg = LogMsg()
        msg.from_record(record)

        return msg


def arg_or_env(name, args, default=None):
    env_name = 'STACKIFY_{0}'.format(name.upper())
    try:
        return args.get(name, os.environ[env_name])
    except KeyError:
        if default:
            return default
        else:
            raise NameError('You must specify the keyword argument {0} or environment variable {1}'.format(
                name, env_name))



class StackifyListener(QueueListener):
    '''
    A listener to read queued log messages and send them to Stackify.
    '''

    def __init__(self, queue_, config=None, **kwargs):
        super(StackifyListener, self).__init__(queue_)

        if config is None:
            # config not specified, build one with kwargs or environment variables
            config = ApiConfiguration(
                application = arg_or_env('application', kwargs),
                environment = arg_or_env('environment', kwargs),
                api_key = arg_or_env('api_key', kwargs),
                api_url = arg_or_env('api_url', kwargs, API_URL))

        self.http = HTTPClient(config)

    def handle(self, record):



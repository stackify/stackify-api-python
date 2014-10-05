import logging
import threading

try:
    from logging.handlers import QueueHandler, QueueListener
except:
    from stackify.handler_backport import QueueHandler, QueueListener

try:
    import Queue as queue
except ImportError:
    import queue

from stackify import QUEUE_SIZE
from stackify.log import LogMsg
from stackify.error import ErrorItem
from stackify.http import HTTPClient



class StackifyHandler(QueueHandler):
    '''
    A handler class to format and queue log messages for later
    transmission to Stackify servers.
    '''

    def __init__(self, queue_=None):
        if queue_ is None:
            queue_ = queue.Queue(QUEUE_SIZE)

        super(StackifyHandler, self).__init__(queue_)

        self.listener = StackifyListener(queue_)

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
        print(record.__dict__)
        msg = LogMsg()
        msg.from_record(record)

        return msg


class StackifyListener(QueueListener):
    '''
    A listener to read queued log messages and send them to Stackify.
    '''

    def __init__(self, queue_):
        super(StackifyListener, self).__init__(queue_)


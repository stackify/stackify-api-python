import logging
import threading
import os

try:
    from logging.handlers import QueueHandler, QueueListener
except: # pragma: no cover
    from stackify.handler_backport import QueueHandler, QueueListener

try:
    import Queue as queue
except ImportError: # pragma: no cover
    import queue

from stackify import QUEUE_SIZE, API_URL, MAX_BATCH
from stackify.log import LogMsg, LogMsgGroup
from stackify.error import ErrorItem
from stackify.http import HTTPClient
from stackify.application import get_configuration


class StackifyHandler(QueueHandler):
    '''
    A handler class to format and queue log messages for later
    transmission to Stackify servers.
    '''

    def __init__(self, queue_=None, listener=None, **kwargs):
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
        logger = logging.getLogger(__name__)
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            logger.warn('StackifyHandler queue is full, evicting oldest record')
            self.queue.get_nowait()
            self.queue.put_nowait(record)


class StackifyListener(QueueListener):
    '''
    A listener to read queued log messages and send them to Stackify.
    '''

    def __init__(self, queue_, max_batch=MAX_BATCH, config=None, **kwargs):
        super(StackifyListener, self).__init__(queue_)

        if config is None:
            config = get_configuration(**kwargs)

        self.max_batch = max_batch
        self.messages = []
        self.http = HTTPClient(config)

    def handle(self, record):
        if not self.http.identified:
            logger = logging.getLogger(__name__)
            logger.debug('Identifying application')
            self.http.identify_application()

        msg = LogMsg()
        msg.from_record(record)
        self.messages.append(msg)

        if len(self.messages) >= self.max_batch:
            self.send_group()

    def send_group(self):
        group = LogMsgGroup(self.messages)
        try:
            self.http.send_log_group(group)
        except:
            logger = logging.getLogger(__name__)
            logger.exception('Could not send %s log messages, discarding', len(self.messages))
        del self.messages[:]

    def stop(self):
        logger = logging.getLogger(__name__)
        logger.debug('Shutting down listener')
        super(StackifyListener, self).stop()

        # send any remaining messages
        if self.messages:
            logger.debug('%s messages left on shutdown, uploading', len(self.messages))
            self.send_group()


import logging
import atexit

try:
    from logging.handlers import QueueHandler, QueueListener
except Exception:  # pragma: no cover
    from stackify.handler_backport import QueueHandler, QueueListener

try:
    import Queue as queue
except ImportError:  # pragma: no cover
    import queue

from stackify.application import get_configuration
from stackify.constants import API_REQUEST_INTERVAL_IN_SEC
from stackify.constants import MAX_BATCH
from stackify.constants import QUEUE_SIZE
from stackify.http import HTTPClient
from stackify.log import LogMsg, LogMsgGroup
from stackify.timer import RepeatedTimer


internal_logger = logging.getLogger(__name__)


class StackifyHandler(QueueHandler):
    '''
    A handler class to format and queue log messages for later
    transmission to Stackify servers.
    '''

    def __init__(self, queue_=None, listener=None, ensure_at_exit=True, **kwargs):
        if queue_ is None:
            queue_ = queue.Queue(QUEUE_SIZE)

        super(StackifyHandler, self).__init__(queue_)

        if listener is None:
            listener = StackifyListener(queue_, **kwargs)

        self.listener = listener
        self.listener.start()

        if ensure_at_exit:
            internal_logger.debug('Registering atexit callback')
            atexit.register(self.listener.stop)

    def enqueue(self, record):
        '''
        Put a new record on the queue. If it's full, evict an item.
        '''
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            internal_logger.warning('StackifyHandler queue is full, evicting oldest record')
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
        self.timer = RepeatedTimer(API_REQUEST_INTERVAL_IN_SEC, self.send_group)

        self._started = False

    def handle(self, record):
        if not self.http.identified:
            internal_logger.debug('Identifying application')
            self.http.identify_application()

        msg = LogMsg()
        msg.from_record(record)
        self.messages.append(msg)

        if len(self.messages) >= self.max_batch:
            self.send_group()

    def send_group(self):
        if not self.messages:
            return

        group = LogMsgGroup(self.messages)
        try:
            self.http.send_log_group(group)
        except Exception:
            internal_logger.exception('Could not send {} log messages, discarding'.format(len(self.messages)))
        del self.messages[:]

    def start(self):
        internal_logger.debug('Starting up listener')

        if not self._started:
            super(StackifyListener, self).start()
            self.timer.start()
            self._started = True

    def stop(self):
        internal_logger.debug('Shutting down listener')

        if self._started:
            super(StackifyListener, self).stop()
            self.timer.stop()
            self._started = False

        # send any remaining messages
        if self.messages:
            internal_logger.debug('{} messages left on shutdown, uploading'.format(len(self.messages)))
            self.send_group()

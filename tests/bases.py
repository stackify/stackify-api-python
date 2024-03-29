import collections
import logging
import os
import retrying
import unittest

old_retry = retrying.retry
_LoggingWatcher = collections.namedtuple("_LoggingWatcher", ["records", "output"])


class ClearEnvTest(unittest.TestCase):
    '''
    This class clears the environment variables that the
    library uses for clean testing.
    '''

    def setUp(self):
        # if you have these specified in the environment it will break tests
        to_save = [
            'STACKIFY_APPLICATION',
            'STACKIFY_ENVIRONMENT',
            'STACKIFY_API_KEY',
            'STACKIFY_API_URL',
            'STACKIFY_TRANSPORT',
            'STACKIFY_TRANSPORT_HTTP_ENDPOINT',
            'RETRACE_RUM_SCRIPT_URL',
            'RETRACE_RUM_KEY'
        ]
        self.saved = {}
        for key in to_save:
            if key in os.environ:
                self.saved[key] = os.environ[key]
                del os.environ[key]

    def tearDown(self):
        # restore deleted environment variables
        for key, item in self.saved.items():
            os.environ[key] = item
        del self.saved


def fake_retry_decorator(retries):
    def fake_retry(*args, **kwargs):
        kwargs['wait_exponential_max'] = 0  # no delay between retries
        kwargs['stop_max_attempt_number'] = retries

        def inner(func):
            return old_retry(*args, **kwargs)(func)
        return inner
    return fake_retry


class _BaseTestCaseContext(object):

    def __init__(self, test_case):
        self.test_case = test_case

    def _raiseFailure(self, standardMsg):
        msg = self.test_case._formatMessage(self.msg, standardMsg)
        raise self.test_case.failureException(msg)


class _CapturingHandler(logging.Handler):
    """
    A logging handler capturing all (raw and formatted) logging output.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.watcher = _LoggingWatcher([], [])

    def flush(self):
        pass

    def emit(self, record):
        self.watcher.records.append(record)
        msg = self.format(record)
        self.watcher.output.append(msg)


class _AssertLogsContext(_BaseTestCaseContext):
    """A context manager used to implement TestCase.assertLogs()."""

    LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"

    def __init__(self, test_case, logger_name, level):
        _BaseTestCaseContext.__init__(self, test_case)
        self.logger_name = logger_name
        if level:
            self.level = logging._levelNames.get(level, level)
        else:
            self.level = logging.INFO
        self.msg = None

    def __enter__(self):
        if isinstance(self.logger_name, logging.Logger):
            logger = self.logger = self.logger_name
        else:
            logger = self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(self.LOGGING_FORMAT)
        handler = _CapturingHandler()
        handler.setFormatter(formatter)
        self.watcher = handler.watcher
        self.old_handlers = logger.handlers[:]
        self.old_level = logger.level
        self.old_propagate = logger.propagate
        logger.handlers = [handler]
        logger.setLevel(self.level)
        logger.propagate = False
        return handler.watcher

    def __exit__(self, exc_type, exc_value, tb):
        self.logger.handlers = self.old_handlers
        self.logger.propagate = self.old_propagate
        self.logger.setLevel(self.old_level)
        if exc_type is not None:
            # let unexpected exceptions pass through
            return False
        if len(self.watcher.records) == 0:
            self._raiseFailure(
                "no logs of level {} or higher triggered on {}"
                .format(logging.getLevelName(self.level), self.logger.name))


class LogTestCase(unittest.TestCase):

    def assertLogs(self, logger=None, level=None):
        """Fail unless a log message of level *level* or higher is emitted
        on *logger_name* or its children.  If omitted, *level* defaults to
        INFO and *logger* defaults to the root logger.

        This method must be used as a context manager, and will yield
        a recording object with two attributes: `output` and `records`.
        At the end of the context manager, the `output` attribute will
        be a list of the matching formatted log messages and the
        `records` attribute will be a list of the corresponding LogRecord
        objects.

        Example::

            with self.assertLogs('foo', level='INFO') as cm:
                logging.getLogger('foo').info('first message')
                logging.getLogger('foo.bar').error('second message')
            self.assertEqual(cm.output, ['INFO:foo:first message',
                                         'ERROR:foo.bar:second message'])
        """
        return _AssertLogsContext(self, logger, level)

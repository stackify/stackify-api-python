import os
import retrying
import unittest


old_retry = retrying.retry


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

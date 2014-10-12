#!/usr/bin/env python
"""
Test the stackify.http module
"""

import unittest
import retrying
from mock import patch, Mock

retrying_mock = Mock()

import stackify.http

from stackify.application import ApiConfiguration


old_retry = retrying.retry

FAKE_RETRIES = 3

def fake_retry(*args, **kwargs):
    kwargs['wait_exponential_max'] = 0 # no delay between retries
    kwargs['stop_max_attempt_number'] = FAKE_RETRIES # stop after 3 tries
    def inner(func):
        return old_retry(*args, **kwargs)(func)
    return inner


class TestClient(unittest.TestCase):
    '''
    Test the HTTP Client and associated utilities
    '''

    @classmethod
    def setUpClass(cls):
        retrying.retry = fake_retry
        reload(stackify.http)

    @classmethod
    def tearDownClass(cls):
        reload(retrying)
        reload(stackify.http)

    def setUp(self):
        self.config = ApiConfiguration(
            application = 'test_appname',
            environment = 'test_environment',
            api_key = 'test_apikey',
            api_url = 'test_apiurl')

    def test_logger_no_config(self):
        '''GZIP encoder works'''
        correct = list('\x1f\x8b\x08\x00    \x02\xff\xf3H\xcd\xc9\xc9\xd7Q(\xcf/\xcaIQ\x04\x00\xe6\xc6\xe6\xeb\r\x00\x00\x00')
        gzipped = list(stackify.http.gzip_compress('Hello, world!'))
        gzipped[4:8] = '    ' # blank the mtime
        self.assertEqual(gzipped, correct)

    def test_identify_retrying(self):
        '''HTTP identify should retry'''
        client = stackify.http.HTTPClient(self.config)

        class CustomException(Exception): pass
        crash = Mock(side_effect=CustomException)

        with patch.object(client, 'POST', crash):
            with self.assertRaises(CustomException):
                client.identify_application()
        self.assertEqual(crash.call_count, FAKE_RETRIES)


if __name__=='__main__':
    unittest.main()


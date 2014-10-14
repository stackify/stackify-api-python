"""
Test the stackify.http module
"""

import unittest
from mock import patch, Mock

import retrying
import stackify.http

from stackify.log import LogMsgGroup
from stackify.application import ApiConfiguration
from stackify import READ_TIMEOUT

old_retry = retrying.retry

def fake_retry_decorator(retries):
    def fake_retry(*args, **kwargs):
        kwargs['wait_exponential_max'] = 0 # no delay between retries
        kwargs['stop_max_attempt_number'] = retries
        def inner(func):
            print '!'*80
            print 'using retrying mock', kwargs
            return old_retry(*args, **kwargs)(func)
        return inner
    return fake_retry


class TestClient(unittest.TestCase):
    '''
    Test the HTTP Client and associated utilities
    '''

    @classmethod
    def setUpClass(cls):
        cls.FAKE_RETRIES = 3
        print '!'*80
        print 'another retry', retrying.retry
        retrying.retry = fake_retry_decorator(cls.FAKE_RETRIES)
        print 'patched retry', retrying.retry
        reload(stackify.http)
        print 'func is', stackify.http.HTTPClient.POST

    @classmethod
    def tearDownClass(cls):
        print '!'*80
        print 'teardown'
        reload(retrying)
        reload(stackify.http)

    def setUp(self):
        self.config = ApiConfiguration(
            application = 'test_appname',
            environment = 'test_environment',
            api_key = 'test_apikey',
            api_url = 'test_apiurl')

        self.client = stackify.http.HTTPClient(self.config)

    def test_logger_no_config(self):
        '''GZIP encoder works'''
        correct = list('\x1f\x8b\x08\x00    \x02\xff\xf3H\xcd\xc9\xc9\xd7Q(\xcf/\xcaIQ\x04\x00\xe6\xc6\xe6\xeb\r\x00\x00\x00')
        gzipped = list(stackify.http.gzip_compress('Hello, world!'))
        gzipped[4:8] = '    ' # blank the mtime
        self.assertEqual(gzipped, correct)

    def test_identify_retrying(self):
        '''HTTP identify should retry'''
        client = self.client

        class CustomException(Exception): pass
        crash = Mock(side_effect=CustomException)

        with patch.object(client, 'POST', crash):
            with self.assertRaises(CustomException):
                client.identify_application()
        self.assertEqual(crash.call_count, self.FAKE_RETRIES)

    def test_identify(self):
        '''HTTP identify should save results'''
        client = self.client
        self.assertFalse(client.identified)

        result = {
            'AppNameID': '1',
            'AppEnvID': '2',
            'DeviceID': '3',
            'DeviceAppID': '4',
            'DeviceAlias': '5',
        }
        post = Mock(return_value=result)

        with patch.object(client, 'POST', post):
            client.identify_application()

        self.assertEqual(client.app_name_id, '1')
        self.assertEqual(client.app_env_id, '2')
        self.assertEqual(client.device_id, '3')
        self.assertEqual(client.device_app_id, '4')
        self.assertEqual(client.device_alias, '5')
        self.assertTrue(client.identified)

    def test_send_log_group_retrying(self):
        '''HTTP sending log groups should retry'''
        client = self.client

        class CustomException(Exception): pass
        crash = Mock(side_effect=CustomException)

        group = LogMsgGroup([])

        with patch.object(client, 'POST', crash):
            with self.assertRaises(CustomException):
                client.send_log_group(group)
        self.assertEqual(crash.call_count, self.FAKE_RETRIES)

    def test_send_log_group(self):
        '''Send log group fills out info and submits ok'''
        client = self.client
        client.identified = True

        client.device_id = 'test_d_id'
        client.device_app_id = 'test_dapp_id'
        client.app_name_id = 'test_name_id'
        client.device_alias = 'test_alias'

        group = LogMsgGroup([])

        with patch.object(client, 'POST') as post:
            client.send_log_group(group)
            self.assertTrue(post.called)

        self.assertEqual(group.CDID, client.device_id)
        self.assertEqual(group.CDAppID, client.device_app_id)
        self.assertEqual(group.AppNameID, client.app_name_id)
        self.assertEqual(group.ServerName, client.device_alias)


    @patch('requests.post')
    def test_post_arguments(self, post):
        '''HTTP post has correct headers'''
        client = self.client
        payload = Mock()

        client.POST('url', payload)

        headers = {
            'Content-Type': 'application/json',
            'X-Stackify-Key': self.config.api_key,
            'X-Stackify-PV': 'V1',
        }

        self.assertTrue(post.called)
        args, kwargs = post.call_args
        self.assertEquals(kwargs['headers'], headers)
        self.assertEquals(kwargs['timeout'], READ_TIMEOUT)
        self.assertEquals(kwargs['data'], payload.toJSON())

    @patch('requests.post')
    def test_post_gzip(self, post):
        '''HTTP post uses gzip if requested'''
        client = self.client
        payload = Mock()
        payload.toJSON = Mock(return_value='1')
        gzip = Mock(side_effect=lambda x: x + '_gzipped')

        with patch.object(stackify.http, 'gzip_compress', gzip):
            client.POST('url', payload, use_gzip=True)

        self.assertTrue(post.called)
        args, kwargs = post.call_args
        self.assertEquals(kwargs['headers']['Content-Encoding'], 'gzip')
        self.assertEquals(kwargs['data'], '1_gzipped')


if __name__=='__main__':
    unittest.main()


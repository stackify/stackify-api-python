"""
Test the stackify.http module
"""

import unittest
from mock import patch, Mock
import imp

import retrying
import stackify.transport.default.http

from stackify.transport.default.log import LogMsgGroup
from stackify.transport.application import ApiConfiguration
from stackify.constants import READ_TIMEOUT
from stackify.transport.application import EnvironmentDetail
from tests.bases import fake_retry_decorator


class TestClient(unittest.TestCase):
    '''
    Test the HTTP Client and associated utilities
    '''

    @classmethod
    def setUpClass(cls):
        cls.FAKE_RETRIES = 3
        retrying.retry = fake_retry_decorator(cls.FAKE_RETRIES)
        imp.reload(stackify.transport.default.http)

    @classmethod
    def tearDownClass(cls):
        imp.reload(retrying)
        imp.reload(stackify.transport.default.http)

    def setUp(self):
        self.config = ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = EnvironmentDetail(self.config)

        self.client = stackify.transport.default.http.HTTPClient(self.config, self.env_details)

    def test_logger_no_config(self):
        '''GZIP encoder works'''
        correct = list(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff\xf3H\xcd\xc9\xc9\xd7Q(\xcf/\xcaIQ\x04\x00\xe6\xc6\xe6\xeb\r\x00\x00\x00')
        gzipped = list(stackify.transport.default.http.gzip_compress('Hello, world!'))
        gzipped[4:8] = b'\x00\x00\x00\x00'  # blank the mtime
        self.assertEqual(gzipped, correct)

    def test_identify_retrying(self):
        '''HTTP identify should retry'''
        client = self.client

        class CustomException(Exception):
            pass

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

        class CustomException(Exception):
            pass

        crash = Mock(side_effect=CustomException)

        group = LogMsgGroup([])

        with patch.object(client, 'POST', crash):
            with self.assertRaises(CustomException):
                client.send_log_group('url', group)
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
            client.send_log_group('url', group)
            self.assertTrue(post.called)

        self.assertEqual(group.CDID, client.device_id)
        self.assertEqual(group.CDAppID, client.device_app_id)
        self.assertEqual(group.AppNameID, client.app_name_id)

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
        self.assertEqual(kwargs['headers'], headers)
        self.assertEqual(kwargs['timeout'], READ_TIMEOUT)
        self.assertEqual(kwargs['data'], payload.toJSON())

    @patch('requests.post')
    def test_post_gzip(self, post):
        '''HTTP post uses gzip if requested'''
        client = self.client
        payload = Mock()
        payload.toJSON = Mock(return_value='1')
        gzip = Mock(side_effect=lambda x: x + '_gzipped')

        with patch.object(stackify.transport.default.http, 'gzip_compress', gzip):
            client.POST('url', payload, use_gzip=True)

        self.assertTrue(post.called)
        args, kwargs = post.call_args
        self.assertEqual(kwargs['headers']['Content-Encoding'], 'gzip')
        self.assertEqual(kwargs['data'], '1_gzipped')


if __name__ == '__main__':
    unittest.main()

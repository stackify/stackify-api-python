"""
Test the stackify.application module
"""

import unittest
from mock import patch
from tests.bases import ClearEnvTest

from stackify.constants import API_URL
from stackify.transport.application import get_configuration


class TestConfig(ClearEnvTest):
    '''
    Test automatic configuration for the ApiConfiguration
    '''

    def test_required_kwargs(self):
        '''API configuration requires appname, env and key'''
        env_map = {}

        with patch.dict('os.environ', env_map):
            with self.assertRaises(NameError):
                get_configuration()
            with self.assertRaises(NameError):
                get_configuration(application='1')
            with self.assertRaises(NameError):
                get_configuration(application='1', environment='2')
            with self.assertRaises(NameError):
                get_configuration(application='1', environment='2', api_url='3')

            get_configuration(application='1', environment='2', api_key='3')

    def test_environment_config(self):
        '''API configuration can load from env vars'''
        env_map = {
            'STACKIFY_APPLICATION': 'test1_appname',
            'STACKIFY_ENVIRONMENT': 'test1_environment',
            'STACKIFY_API_KEY': 'test1_apikey',
            'STACKIFY_API_URL': 'test1_apiurl',
        }

        with patch.dict('os.environ', env_map):
            config = get_configuration()

        self.assertEqual(config.application, 'test1_appname')
        self.assertEqual(config.environment, 'test1_environment')
        self.assertEqual(config.api_key, 'test1_apikey')
        self.assertEqual(config.api_url, 'test1_apiurl')

    def test_kwarg_mix(self):
        '''API configuration can load from a mix of env vars and kwargs'''
        env_map = {
            'STACKIFY_APPLICATION': 'test2_appname',
            'STACKIFY_ENVIRONMENT': 'test2_environment',
        }

        with patch.dict('os.environ', env_map):
            config = get_configuration(api_key='test2_apikey', api_url='test2_apiurl')

        self.assertEqual(config.application, 'test2_appname')
        self.assertEqual(config.environment, 'test2_environment')
        self.assertEqual(config.api_key, 'test2_apikey')
        self.assertEqual(config.api_url, 'test2_apiurl')

    def test_kwargs(self):
        '''API configuration can load from kwargs'''
        config = get_configuration(
            application='test3_appname',
            environment='test3_environment',
            api_key='test3_apikey',
            api_url='test3_apiurl',
        )

        self.assertEqual(config.application, 'test3_appname')
        self.assertEqual(config.environment, 'test3_environment')
        self.assertEqual(config.api_key, 'test3_apikey')
        self.assertEqual(config.api_url, 'test3_apiurl')

    def test_api_url_default(self):
        '''API URL is set automatically'''
        config = get_configuration(
            application='test4_appname',
            environment='test4_environment',
            api_key='test4_apikey',
        )

        self.assertEqual(config.application, 'test4_appname')
        self.assertEqual(config.environment, 'test4_environment')
        self.assertEqual(config.api_key, 'test4_apikey')
        self.assertEqual(config.api_url, API_URL)

    def test_transport_default(self):
        config = get_configuration(
            application='test4_appname',
            environment='test4_environment',
            api_key='test4_apikey',
            api_url='test3_apiurl',
        )

        self.assertEqual(config.application, 'test4_appname')
        self.assertEqual(config.environment, 'test4_environment')
        self.assertEqual(config.api_key, 'test4_apikey')
        self.assertEqual(config.api_url, 'test3_apiurl')
        self.assertEqual(config.transport, 'default')

    def test_transport_given(self):
        config = get_configuration(
            application='test5_appname',
            environment='test5_environment',
            api_key='test5_apikey',
            api_url='test5_apiurl',
            transport='test5_transport'
        )

        self.assertEqual(config.application, 'test5_appname')
        self.assertEqual(config.environment, 'test5_environment')
        self.assertEqual(config.api_key, 'test5_apikey')
        self.assertEqual(config.api_url, 'test5_apiurl')
        self.assertEqual(config.transport, 'test5_transport')


if __name__ == '__main__':
    unittest.main()

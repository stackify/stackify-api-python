"""
Test the stackify.application module
"""

import unittest
import os
from mock import patch
from tests.bases import ClearEnvTest

from stackify.constants import API_URL
from stackify.constants import DEFAULT_HTTP_ENDPOINT
from stackify.constants import TRANSPORT_TYPE_AGENT_HTTP
from stackify.constants import TRANSPORT_TYPE_AGENT_SOCKET
from stackify.constants import TRANSPORT_TYPE_DEFAULT
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

    def test_api_key_is_required_on_default_transport(self):
        with self.assertRaises(NameError):
            get_configuration(
                application='test_appname',
                environment='test_environment',
                api_key='',
                api_url='test_apiurl',
                transport='default'
            )

    def test_api_key_is_not_required_on_agent_socket_transport(self):
        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='',
            api_url='test_apiurl',
            transport='agent_socket'
        )

        self.assertEqual(config.application, 'test_appname')
        self.assertEqual(config.environment, 'test_environment')
        self.assertEqual(config.api_key, '')
        self.assertEqual(config.api_url, 'test_apiurl')
        self.assertEqual(config.transport, 'agent_socket')


class ConfigEnvironmentVariableTest(ClearEnvTest):
    def test_transport_environment_variable_default(self):
        os.environ["STACKIFY_TRANSPORT"] = "default"

        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )

        assert config.transport == TRANSPORT_TYPE_DEFAULT

        del os.environ["STACKIFY_TRANSPORT"]

    def test_transport_environment_variable_agent_socket(self):
        os.environ["STACKIFY_TRANSPORT"] = "agent_socket"

        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )

        assert config.transport == TRANSPORT_TYPE_AGENT_SOCKET

        del os.environ["STACKIFY_TRANSPORT"]

    def test_transport_environment_variable_agent_http(self):
        os.environ["STACKIFY_TRANSPORT"] = "agent_http"

        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )

        assert config.transport == TRANSPORT_TYPE_AGENT_HTTP

        del os.environ["STACKIFY_TRANSPORT"]

    def test_http_endpoint_environment_variable_default(self):
        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )

        assert config.http_endpoint == DEFAULT_HTTP_ENDPOINT

    def test_http_endpoint_environment_variable(self):
        os.environ["STACKIFY_TRANSPORT_HTTP_ENDPOINT"] = "test"

        config = get_configuration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )

        assert config.http_endpoint == "test"

        del os.environ["STACKIFY_TRANSPORT_HTTP_ENDPOINT"]


if __name__ == '__main__':
    unittest.main()

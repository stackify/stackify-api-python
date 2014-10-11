#!/usr/bin/env python
"""
Test the stackify.application module
"""

import unittest
from mock import patch

from stackify.application import get_configuration


class TestConfig(unittest.TestCase):
    def test_environment_config(self):
        env_map = {
            'STACKIFY_APPLICATION': 'test_appname',
            'STACKIFY_ENVIRONMENT': 'test_environment',
            'STACKIFY_API_KEY': 'test_apikey',
            'STACKIFY_API_URL': 'test_apiurl',
        }

        with patch.dict('os.environ', env_map):
            config = get_configuration()

        self.assertEqual(config.application, 'test_appname')
        self.assertEqual(config.environment, 'test_environment')
        self.assertEqual(config.api_key, 'test_apikey')
        self.assertEqual(config.api_url, 'test_apiurl')

    def test_kwarg_mix(self):
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
        config = get_configuration(
                    application = 'test3_appname',
                    environment = 'test3_environment',
                    api_key = 'test3_apikey',
                    api_url = 'test3_apiurl')

        self.assertEqual(config.application, 'test3_appname')
        self.assertEqual(config.environment, 'test3_environment')
        self.assertEqual(config.api_key, 'test3_apikey')
        self.assertEqual(config.api_url, 'test3_apiurl')


if __name__=='__main__':
    unittest.main()


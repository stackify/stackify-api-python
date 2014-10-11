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


if __name__=='__main__':
    unittest.main()


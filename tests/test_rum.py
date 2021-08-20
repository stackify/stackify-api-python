try:
    from unittest import mock
except Exception:
    import mock # noqa F401

import stackify
import os
import stackify.rum
import json

from .bases import ClearEnvTest
from stackify.transport.application import ApiConfiguration
from stackify.utils import arg_or_env
from stackify.constants import DEFAULT_RUM_SCRIPT_URL
from unittest import TestCase

APM_CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "RUM_SCRIPT_URL": "https://test.com/test.js",
    "RUM_KEY": "LOREM123"
}


class RumTest(TestCase):
    def setUp(self):
        self.config_rum_key = stackify.config.rum_key
        self.config_rum_script_url = stackify.config.rum_script_url
        self.config_application = stackify.config.application
        self.config_environment = stackify.config.environment
        self.maxDiff = None

    def shutDown(self):
        pass

    @mock.patch('stackify.rum.is_apm_installed')
    @mock.patch('stackify.rum.get_reporting_url')
    @mock.patch('stackify.rum.get_transaction_id')
    def test_default_insert_rum_script(self, func, func_reporting_url, func_apm):
        func.return_value = '123'
        func_reporting_url.return_value = 'test reporting url'
        func_apm.return_value = False
        self.update_common_config(
            rum_key='asd',
            application='app',
            environment='env'
        )

        rum_settings = {
            "ID": '123',
            "Name": 'YXBw',
            "Env": 'ZW52',
            "Trans": 'dGVzdCByZXBvcnRpbmcgdXJs'
        }

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()

        assert result == '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="https://stckjs.stackify.com/stckjs.js" data-key="asd" async></script>'.format(json.dumps(rum_settings))

    @mock.patch('stackify.rum.is_apm_installed')
    def test_default_insert_rum_script_no_transaction_id(self, func_apm):
        func_apm.return_value = False
        self.update_common_config(
            rum_key='asd',
            application='app',
            environment='env'
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()

        assert not result
        assert result is ''

    @mock.patch('stackify.rum.is_apm_installed')
    def test_default_insert_rum_script_no_key(self, func_apm):
        func_apm.return_value = False
        self.update_common_config(
            rum_key='',
            application='app',
            environment='env'
        )

        result = stackify.rum.insert_rum_script()
        assert not result
        assert result is ''

        self.reset_common_config()

    @mock.patch('stackify.rum.is_apm_installed')
    def test_default_insert_rum_script_no_details(self, func_apm):
        func_apm.return_value = False
        self.update_common_config()

        result = stackify.rum.insert_rum_script()
        assert not result
        assert result is ''

        self.reset_common_config()

    @mock.patch('stackify.rum.is_apm_installed')
    @mock.patch('stackify.rum.get_reporting_url')
    @mock.patch('stackify.rum.get_transaction_id')
    def test_default_insert_rum_script_from_api(self, func, func_reporting_url, func_apm):
        func.return_value = '123'
        func_apm.return_value = False
        func_reporting_url.return_value = 'test reporting url'
        self.create_config(
            rum_key='asd1',
            application='app1',
            environment='env1'
        )
        rum_settings = {
            "ID": '123',
            "Name": 'YXBwMQ==',
            "Env": 'ZW52MQ==',
            "Trans": 'dGVzdCByZXBvcnRpbmcgdXJs'
        }
        result = stackify.rum.insert_rum_script()
        self.reset_common_config()
        assert result == '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="https://stckjs.stackify.com/stckjs.js" data-key="asd1" async></script>'.format(json.dumps(rum_settings))

    @mock.patch('stackify.rum.is_apm_installed')
    def test_default_insert_rum_script_no_key_from_api(self, func_apm):
        func_apm.return_value = False
        self.create_config(
            rum_key=None,
            application='app2',
            environment='env2'
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()

        assert not result
        assert result is ''

    @mock.patch('stackify.rum.is_apm_installed')
    def test_default_insert_rum_script_no_details_from_api(self, func_apm):
        func_apm.return_value = False
        self.create_config(
            application=None,
            environment=None,
            rum_key=None
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()

        assert not result
        assert result is ''

    def update_common_config(self, rum_key=None, rum_script_url=None, application=None, environment=None):
        self.config_rum_key = stackify.config.rum_key
        self.config_rum_script_url = stackify.config.rum_script_url
        self.config_application = stackify.config.application
        self.config_environment = stackify.config.environment

        if rum_key is not None:
            stackify.config.rum_key = rum_key
        if rum_script_url is not None:
            stackify.config.rum_script_url = rum_script_url
        if application is not None:
            stackify.config.application = application
        if environment is not None:
            stackify.config.environment = environment

    def reset_common_config(self):
        stackify.config.rum_key = self.config_rum_key
        stackify.config.rum_script_url = self.config_rum_script_url
        stackify.config.application = self.config_application
        stackify.config.environment = self.config_environment

    def create_config(self, **kwargs):
        return ApiConfiguration(
            application=kwargs['application'],
            environment=kwargs['environment'],
            api_key='test_apikey',
            api_url='test_apiurl',
            rum_script_url=arg_or_env('rum_script_url', kwargs, DEFAULT_RUM_SCRIPT_URL, env_key='RETRACE_RUM_SCRIPT_URL'),
            rum_key=arg_or_env('rum_key', kwargs, DEFAULT_RUM_SCRIPT_URL, env_key='RETRACE_RUM_KEY')
        )


class RumConfigurationTest(ClearEnvTest):
    '''
    Test the logger init functionality
    '''

    def setUp(self):
        super(RumConfigurationTest, self).setUp()
        self.config_rum_key = stackify.config.rum_key
        self.config_rum_script_url = stackify.config.rum_script_url
        self.config_application = stackify.config.application
        self.config_environment = stackify.config.environment

    def tearDown(self):
        super(RumConfigurationTest, self).tearDown()

    def test_rum_script_url_valid(self):
        os.environ["RETRACE_RUM_SCRIPT_URL"] = 'https://test.com/test.js'
        config = self.create_config()
        assert config.rum_script_url == 'https://test.com/test.js'
        del os.environ["RETRACE_RUM_SCRIPT_URL"]
        self.reset_common_config()

    @mock.patch('logging.Logger.exception')
    def test_rum_script_url_invalid(self, func=None):
        os.environ["RETRACE_RUM_SCRIPT_URL"] = 'asd'
        config = self.create_config()
        assert config.rum_script_url == 'https://stckjs.stackify.com/stckjs.js'  # Default
        del os.environ["RETRACE_RUM_SCRIPT_URL"]
        self.reset_common_config()
        func.assert_called_with('https://stckjs.stackify.com/stckjs.js does not match pattern ^[A-Za-z0-9_-]+$')

    def test_rum_key_valid(self):
        os.environ["RETRACE_RUM_KEY"] = 'TEST123-_'
        config = self.create_config()
        assert config.rum_key == 'TEST123-_'
        del os.environ["RETRACE_RUM_KEY"]
        self.reset_common_config()

    @mock.patch('logging.Logger.exception')
    def test_rum_key_invalid(self, func=None):
        os.environ["RETRACE_RUM_KEY"] = 'asd`1!'
        config = self.create_config()
        assert config.rum_key == ''  # Default
        del os.environ["RETRACE_RUM_KEY"]
        self.reset_common_config()
        func.assert_called_with('asd`1! does not match pattern ^[A-Za-z0-9_-]+$')

    def create_config(self, **kwargs):
        return ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
            rum_script_url=arg_or_env('rum_script_url', kwargs, DEFAULT_RUM_SCRIPT_URL, env_key='RETRACE_RUM_SCRIPT_URL'),
            rum_key=arg_or_env('rum_key', kwargs, DEFAULT_RUM_SCRIPT_URL, env_key='RETRACE_RUM_KEY')
        )

    def reset_common_config(self):
        stackify.config.rum_key = self.config_rum_key
        stackify.config.rum_script_url = self.config_rum_script_url
        stackify.config.application = self.config_application
        stackify.config.environment = self.config_environment

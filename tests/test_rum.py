try:
    from unittest import mock
except Exception:
    import mock # noqa F401

import stackify
import os
import stackify.rum
import base64
import json

from .bases import ClearEnvTest
from stackify.transport.application import ApiConfiguration
from stackify.utils import arg_or_env
from stackify.constants import DEFAULT_RUM_SCRIPT_URL
from stackifyapm.base import Client
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

    def test_default_insert_rum_script_from_apm_with_transaction(self):
        self.update_apm_installed(True)
        client = Client(APM_CONFIG)

        transaction = client.begin_transaction("transaction_test", client=client)
        rum_data = stackify.rum.insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(APM_CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(APM_CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode('/'.encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            APM_CONFIG["RUM_SCRIPT_URL"],
            APM_CONFIG["RUM_KEY"]
        )

        assert rum_data == result_string
        client.end_transaction("transaction_test")
        self.restore_apm_installed()

    def test_default_insert_rum_script_from_apm_without_transaction(self):
        self.update_apm_installed(True)
        rum_data = stackify.rum.insert_rum_script()
        assert not rum_data
        self.restore_apm_installed()

    @mock.patch('stackify.rum.get_reporting_url')
    @mock.patch('stackify.rum.get_transaction_id')
    def test_default_insert_rum_script(self, func, func_reporting_url):
        func.return_value = '123'
        func_reporting_url.return_value = 'test reporting url'
        self.update_apm_installed(False)
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
        self.restore_apm_installed()

        assert result == '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="https://stckjs.stackify.com/stckjs.js" data-key="asd" async></script>'.format(json.dumps(rum_settings))

    def test_default_insert_rum_script_no_transaction_id(self):
        self.update_apm_installed(False)
        self.update_common_config(
            rum_key='asd',
            application='app',
            environment='env'
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()
        self.restore_apm_installed()

        assert result is None

    def test_default_insert_rum_script_no_key(self):
        self.update_apm_installed(False)
        self.update_common_config(
            rum_key='',
            application='app',
            environment='env'
        )

        result = stackify.rum.insert_rum_script()
        assert not result

        self.reset_common_config()
        self.restore_apm_installed()

    def test_default_insert_rum_script_no_details(self):
        self.update_apm_installed(False)
        self.update_common_config()

        result = stackify.rum.insert_rum_script()
        assert not result

        self.reset_common_config()
        self.restore_apm_installed()

    @mock.patch('stackify.rum.get_reporting_url')
    @mock.patch('stackify.rum.get_transaction_id')
    def test_default_insert_rum_script_from_api(self, func, func_reporting_url):
        func.return_value = '123'
        func_reporting_url.return_value = 'test reporting url'
        self.update_apm_installed(False)
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
        self.restore_apm_installed()
        assert result == '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="https://stckjs.stackify.com/stckjs.js" data-key="asd1" async></script>'.format(json.dumps(rum_settings))

    def test_default_insert_rum_script_no_key_from_api(self):
        self.update_apm_installed(False)
        self.create_config(
            rum_key=None,
            application='app2',
            environment='env2'
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()
        self.restore_apm_installed()

        assert not result

    def test_default_insert_rum_script_no_details_from_api(self):
        self.update_apm_installed(False)
        self.create_config(
            application=None,
            environment=None,
            rum_key=None
        )

        result = stackify.rum.insert_rum_script()
        self.reset_common_config()
        self.restore_apm_installed()

        assert not result

    def update_apm_installed(self, installed):
        self.apm_installed = stackify.rum.apm_installed
        stackify.rum.apm_installed = installed

    def restore_apm_installed(self):
        stackify.rum.apm_installed = self.apm_installed

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

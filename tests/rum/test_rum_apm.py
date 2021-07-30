try:
    from unittest import mock
except Exception:
    import mock # noqa F401

import stackify
import stackify.rum
import base64
import json
from unittest import TestCase

apmExist = False
try:
    from stackifyapm.base import Client
    apmExist = True
except (ImportError):
    pass

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


class RumTestApm(TestCase):
    def setUp(self):
        self.config_rum_key = stackify.config.rum_key
        self.config_rum_script_url = stackify.config.rum_script_url
        self.config_application = stackify.config.application
        self.config_environment = stackify.config.environment
        self.maxDiff = None

    def shutDown(self):
        pass

    def test_default_insert_rum_script_from_apm_with_transaction(self):
        if not apmExist:
            return

        client = Client(APM_CONFIG)
        print('config')
        print(client.config.rum_key)

        transaction = client.begin_transaction("transaction_test", client=client)
        rum_data = stackify.rum.insert_rum_script()

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

        assert rum_data
        assert rum_data == result_string
        client.end_transaction("transaction_test")

    def test_default_insert_rum_script_from_apm_without_transaction(self):
        if not apmExist:
            return

        rum_data = stackify.rum.insert_rum_script()
        assert not rum_data

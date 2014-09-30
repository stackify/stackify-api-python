import json
import urllib2
import retrying
import logging

from stackify.application import EnvironmentDetail
from stackify import READ_TIMEOUT


internal_log = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self, api_config):
        self.api_config = api_config
        self.environment_detail = EnvironmentDetail(api_config)
        self.identify_application()


    def POST(self, url, payload):
        request_url = self.api_config.api_url + url
        request = urllib2.Request(request_url)
        internal_log.debug('Request URL: {0}'.format(request_url))

        request.add_header('Content-Type', 'application/json')
        request.add_header('X-Stackify-Key', self.api_config.api_key)
        request.add_header('X-Stackify-PV', 'V1')

        try:
            response = urllib2.urlopen(request, json.dumps(payload), timeout=READ_TIMEOUT)
            body = response.read()
            internal_log.debug('Response: {0}'.format(body))
            json.loads('junk')
            return json.loads(body)
        except urllib2.HTTPError as e:
            internal_log.exception('HTTP response: {0}'.format(e.code))
            raise
        except urllib2.URLError as e:
            internal_log.exception('URL exception: {0}'.format(e.reason))
            raise
        except ValueError as e:
            # could not read json response
            internal_log.exception('Cannot decode JSON response')
            raise

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def identify_application(self):
        result = self.POST('/Metrics/IdentifyApp', self.environment_detail.__dict__)
        self.app_name_id = result.get('AppNameID')
        self.app_env_id = result.get('AppEnvID')
        self.device_id = result.get('DeviceID')
        self.device_app_id = result.get('DeviceAppID')


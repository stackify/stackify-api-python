import requests
import retrying
import logging
import gzip

try:
    from cStringIO import StringIO
except Exception:
    try:
        from StringIO import StringIO
    except Exception:
        pass  # python 3, we use a new function in gzip

from stackify.constants import IDENTIFY_URL
from stackify.constants import READ_TIMEOUT


internal_logger = logging.getLogger(__name__)


def gzip_compress(data):
    if hasattr(gzip, 'compress'):
        return gzip.compress(bytes(data, 'utf-8'))  # python 3
    else:
        s = StringIO()
        g = gzip.GzipFile(fileobj=s, mode='w')
        g.write(data)
        g.close()
        return s.getvalue()


class HTTPClient:
    def __init__(self, api_config, env_detail):
        self.api_config = api_config
        self.environment_detail = env_detail
        self.app_name_id = None
        self.app_env_id = None
        self.device_id = None
        self.device_app_id = None
        self.device_alias = None
        self.identified = False

    def POST(self, url, json_object, use_gzip=False):
        request_url = self.api_config.api_url + url
        internal_logger.debug('Request URL: {}'.format(request_url))

        headers = {
            'Content-Type': 'application/json',
            'X-Stackify-Key': self.api_config.api_key,
            'X-Stackify-PV': 'V1',
        }

        try:
            payload_data = json_object.toJSON()
            internal_logger.debug('POST data: {}'.format(payload_data))

            if use_gzip:
                headers['Content-Encoding'] = 'gzip'
                payload_data = gzip_compress(payload_data)

            response = requests.post(request_url,
                                     data=payload_data,
                                     headers=headers,
                                     timeout=READ_TIMEOUT)
            internal_logger.debug('Response: {}'.format(response.text))
            return response.json()
        except requests.exceptions.RequestException:
            internal_logger.exception('HTTP exception')
        except ValueError:
            # could not read json response
            internal_logger.exception('Cannot decode JSON response')

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=32000)
    def identify_application(self):
        internal_logger.debug('Identifying application')
        result = self.POST(IDENTIFY_URL, self.environment_detail)
        self.app_name_id = result.get('AppNameID')
        self.app_env_id = result.get('AppEnvID')
        self.device_id = result.get('DeviceID')
        self.device_app_id = result.get('DeviceAppID')
        self.device_alias = result.get('DeviceAlias')
        self.identified = True

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=32000)
    def send_log_group(self, url, group):
        internal_logger.debug('Sending logs by group')
        group.AppName = self.environment_detail.configuredAppName
        group.Env = self.environment_detail.configuredEnvironmentName
        group.CDID = self.device_id
        group.CDAppID = self.device_app_id
        group.AppNameID = self.app_name_id
        group.ServerName = group.ServerName or self.environment_detail.deviceName
        self.POST(url, group, True)

    def send(self, url, group):
        if not self.identified:
            self.identify_application()

        self.send_log_group(url, group)

import requests
import retrying
import logging
import gzip

try:
    from cStringIO import StringIO
except:
    try:
        from StringIO import StringIO
    except:
        pass  # python 3, we use a new function in gzip


def gzip_compress(data):
    if hasattr(gzip, 'compress'):
        return gzip.compress(bytes(data, 'utf-8'))  # python 3
    else:
        s = StringIO()
        g = gzip.GzipFile(fileobj=s, mode='w')
        g.write(data)
        g.close()
        return s.getvalue()


from stackify.application import EnvironmentDetail
from stackify import READ_TIMEOUT


class HTTPClient:
    def __init__(self, api_config):
        self.api_config = api_config
        self.environment_detail = EnvironmentDetail(api_config)
        self.app_name_id = None
        self.app_env_id = None
        self.device_id = None
        self.device_app_id = None
        self.device_alias = None
        self.identified = False

    def POST(self, url, json_object, use_gzip=False):
        request_url = self.api_config.api_url + url
        logger = logging.getLogger(__name__)
        logger.debug('Request URL: %s', request_url)

        headers = {
            'Content-Type': 'application/json',
            'X-Stackify-Key': self.api_config.api_key,
            'X-Stackify-PV': 'V1',
        }

        try:
            payload_data = json_object.toJSON()
            logger.debug('POST data: %s', payload_data)

            if use_gzip:
                headers['Content-Encoding'] = 'gzip'
                payload_data = gzip_compress(payload_data)

            response = requests.post(request_url,
                                     data=payload_data,
                                     headers=headers,
                                     timeout=READ_TIMEOUT)
            logger.debug('Response: %s', response.text)
            return response.json()
        except requests.exceptions.RequestException:
            logger.exception('HTTP exception')
            raise
        except ValueError as e:
            # could not read json response
            logger.exception('Cannot decode JSON response')
            raise

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def identify_application(self):
        result = self.POST('/Metrics/IdentifyApp', self.environment_detail)
        self.app_name_id = result.get('AppNameID')
        self.app_env_id = result.get('AppEnvID')
        self.device_id = result.get('DeviceID')
        self.device_app_id = result.get('DeviceAppID')
        self.device_alias = result.get('DeviceAlias')
        self.identified = True

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def send_log_group(self, group):
        group.CDID = self.device_id
        group.CDAppID = self.device_app_id
        group.AppNameID = self.app_name_id
        group.ServerName = self.device_alias
        if not group.ServerName:
            group.ServerName = self.environment_detail.deviceName
        self.POST('/Log/Save', group, True)

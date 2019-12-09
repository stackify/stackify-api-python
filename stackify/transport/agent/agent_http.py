import logging
import requests
import retrying

internal_logger = logging.getLogger(__name__)


class AgentHTTP(object):
    """
    AgentHTTP class that handles HTTP post requests
    """

    def _post(self, url, payload):
        headers = {
            'Content-Type': 'application/x-protobuf',
        }
        try:
            return requests.post(url, payload, headers=headers, verify=False)
        except Exception as e:
            internal_logger.debug('HTTP transport exception: {}.'.format(e))
            raise

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=32000)
    def send(self, url, payload):
        # send payload through socket domain using _post method
        return self._post(url, payload)

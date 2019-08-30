import logging
import os
import retrying
import requests_unixsocket


internal_logger = logging.getLogger(__name__)


class AgentSocket(object):
    SOCKET_LOG_FILE = 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock'
    SOCKET_SCHEME = 'http+unix://'

    def __init__(self):
        self._session = requests_unixsocket.Session()

    def post(self, url, payload):
        if not url.startswith(self.SOCKET_SCHEME):
            url = os.path.join(self.SOCKET_LOG_FILE, url.lstrip('/'))

        internal_logger.debug('Request URL: {}'.format(url))
        internal_logger.debug('POST data: {}'.format(payload))

        headers = {
            'Content-Type': 'application/x-protobuf',
        }

        try:
            response = self._session.post(url, payload, headers=headers)
            internal_logger.debug('Response status: {}'.format(response.status_code))
            return response
        except Exception as e:
            internal_logger.debug('HTTP UNIX Socket domain exception: {}.'.format(e))
            raise

    def get(self, url):
        raise NotImplementedError

    def put(self, url, payload):
        raise NotImplementedError

    def patch(self, url, payload):
        raise NotImplementedError

    def delete(self, url, id):
        raise NotImplementedError

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=10000)
    def send(self, url, payload):
        self.post(url, payload)

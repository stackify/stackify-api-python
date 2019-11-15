import logging
import requests
import retrying

from stackify.constants import AGENT_LOG_URL
from stackify.transport.agent.agent_socket import AgentSocket
from stackify.transport.base import AgentBaseTransport

internal_logger = logging.getLogger(__name__)


class AgentSocketTransport(AgentBaseTransport):
    _transport = None

    def __init__(self, api_config, env_details):
        super(AgentSocketTransport, self).__init__(api_config, env_details)
        self._transport = AgentSocket()

    def send(self, group_message):
        self._transport.send(
            self._api_config.socket_url + AGENT_LOG_URL,
            group_message.SerializeToString(),
        )


class AgentHTTPTransport(AgentBaseTransport):
    def __init__(self, api_config, env_details):
        super(AgentHTTPTransport, self).__init__(api_config, env_details)

    def send(self, group_message):
        self._post(
            self._api_config.http_endpoint + AGENT_LOG_URL,
            group_message.SerializeToString(),
        )

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=32000)
    def _post(self, url, payload):
        headers = {
            'Content-Type': 'application/x-protobuf',
        }
        print('url: {}'.format(url))
        try:
            return requests.post(url, payload, headers=headers)
        except Exception as e:
            internal_logger.debug('HTTP transport exception: {}.'.format(e))
            raise

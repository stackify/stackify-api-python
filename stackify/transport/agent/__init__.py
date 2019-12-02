import logging

from stackify.constants import AGENT_LOG_URL
from stackify.transport.agent import agent_http
from stackify.transport.agent import agent_socket
from stackify.transport.base import AgentBaseTransport

internal_logger = logging.getLogger(__name__)


class AgentSocketTransport(AgentBaseTransport):
    """
    Agent Socket Transport handles sending of logs using Unix Socket Domain
    """

    def __init__(self, api_config, env_details):
        super(AgentSocketTransport, self).__init__(api_config, env_details)
        self.url = api_config.socket_url + AGENT_LOG_URL
        self._transport = agent_socket.AgentSocket()


class AgentHTTPTransport(AgentBaseTransport):
    """
    Agent HTTP Transport handles sending of logs using HTTP requests
    """

    def __init__(self, api_config, env_details):
        super(AgentHTTPTransport, self).__init__(api_config, env_details)
        self.url = api_config.http_endpoint + AGENT_LOG_URL
        self._transport = agent_http.AgentHTTP()

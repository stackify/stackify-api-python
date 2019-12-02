import logging

from stackify.constants import TRANSPORT_TYPE_AGENT_HTTP
from stackify.constants import TRANSPORT_TYPE_AGENT_SOCKET
from stackify.constants import TRANSPORT_TYPE_DEFAULT
from stackify.transport.agent import AgentSocketTransport
from stackify.transport.agent import AgentHTTPTransport
from stackify.transport.application import get_configuration
from stackify.transport.application import EnvironmentDetail
from stackify.transport.default import DefaultTransport


internal_logger = logging.getLogger(__name__)


class TransportTypes(object):
    """
    Transport Type class that will determine which transport to use
    depending on users config.

    Types:
    * DEFAULT - HTTP transport that will directly send logs to the Platform
    * AGENT_SOCKET - HTTP warapped Unix Socket Domain that will send logs to the StackifyAgent
    * AGENT_HTTP - HTTP transport that will send logs to the Agent using HTTP requests
    """

    DEFAULT = TRANSPORT_TYPE_DEFAULT
    AGENT_SOCKET = TRANSPORT_TYPE_AGENT_SOCKET
    AGENT_HTTP = TRANSPORT_TYPE_AGENT_HTTP

    @classmethod
    def get_transport(self, api_config=None, env_details=None):
        # determine which transport to use depening on users config
        if api_config.transport == self.AGENT_SOCKET:
            internal_logger.debug('Setting Agent Socket Transport.')
            return AgentSocketTransport(api_config, env_details)

        if api_config.transport == self.AGENT_HTTP:
            internal_logger.debug('Setting Agent HTTP Transport.')
            return AgentHTTPTransport(api_config, env_details)

        internal_logger.debug('Setting Default Transport.')
        api_config.transport = self.DEFAULT
        return DefaultTransport(api_config, env_details)


def configure_transport(config=None, **kwargs):
    # return which transport to use depending on users input
    api_config = config or get_configuration(**kwargs)
    env_details = EnvironmentDetail(api_config)
    return TransportTypes.get_transport(
        api_config,
        env_details,
    )

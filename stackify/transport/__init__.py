import logging

from stackify.constants import LOG_SAVE_URL
from stackify.constants import SOCKET_LOG_URL
from stackify.constants import TRANSPORT_TYPE_AGENT_SOCKET
from stackify.constants import TRANSPORT_TYPE_DEFAULT
from stackify.transport.agent import AgentSocket
from stackify.transport.agent.message import Log
from stackify.transport.agent.message import LogGroup
from stackify.transport.application import get_configuration
from stackify.transport.application import EnvironmentDetail
from stackify.transport.default import HTTPClient
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup

internal_logger = logging.getLogger(__name__)


class TransportTypes(object):
    """
    Transport Type class that will determine which transport to use
    depending on users config.

    Types:
    * DEFAULT - HTTP transport that will directly send logs to the Platform
    * AGENT_SOCKET - HTTP warapped Unix Socket Domain that will send logs to the StackifyAgent
    """

    DEFAULT = TRANSPORT_TYPE_DEFAULT
    AGENT_SOCKET = TRANSPORT_TYPE_AGENT_SOCKET

    @classmethod
    def get_transport(self, api_config=None, env_details=None):
        if api_config.transport == self.AGENT_SOCKET:
            internal_logger.debug('Setting Agent Socket Transport.')
            api_config.transport = self.AGENT_SOCKET
            return AgentSocket()

        internal_logger.debug('Setting Default Transport.')
        api_config.transport = self.DEFAULT
        return HTTPClient(api_config, env_details)

    @classmethod
    def create_message(self, record, api_config, env_details):
        if api_config.transport == self.AGENT_SOCKET:
            return Log(record, api_config, env_details).get_object()

        msg = LogMsg()
        msg.from_record(record)
        return msg

    @classmethod
    def create_group_message(self, messages, api_config, env_details):
        if api_config.transport == self.AGENT_SOCKET:
            return LogGroup(messages, api_config, env_details).get_object()

        return LogMsgGroup(messages)

    @classmethod
    def get_log_url(self, api_config):
        if api_config.transport == self.AGENT_SOCKET:
            return api_config.socket_url + SOCKET_LOG_URL

        return LOG_SAVE_URL

    @classmethod
    def prepare_message(self, api_config, message):
        if api_config.transport == self.AGENT_SOCKET:
            return message.SerializeToString()

        return message


class Transport(object):
    """
    Transport base class
    """

    def __init__(self, config=None, **kwargs):
        self.api_config = config or get_configuration(**kwargs)
        self.env_details = EnvironmentDetail(self.api_config)
        self._transport = TransportTypes.get_transport(
            self.api_config,
            self.env_details,
        )

    def create_message(self, record):
        return TransportTypes.create_message(
            record,
            self.api_config,
            self.env_details,
        )

    def create_group_message(self, messages):
        return TransportTypes.create_group_message(
            messages,
            self.api_config,
            self.env_details,
        )

    def send(self, group_message):
        try:
            self._transport.send(
                TransportTypes.get_log_url(self.api_config),
                TransportTypes.prepare_message(self.api_config, group_message),
            )
        except Exception as e:
            internal_logger.error('Request error: {}'.format(e))

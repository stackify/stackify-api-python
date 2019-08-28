from stackify.constants import SOCKET_LOG_URL
from stackify.constants import LOG_SAVE_URL
from stackify.transport.agent import AgentSocket
from stackify.transport.agent.message import Log
from stackify.transport.agent.message import LogGroup
from stackify.transport.application import get_configuration
from stackify.transport.application import EnvironmentDetail
from stackify.transport.default import HTTPClient
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup
from stackify.utils import arg_or_env


class TransportTypes(object):
    """
    Transport Type class that will determine which transport to use
    depending on users config.

    Types:
    * DEFAULT - HTTP transport that will directly send logs to the Platform
    * AGENT_SOCKET - HTTP warapped Unix Socket Domain that will send logs to the StackifyAgent
    """

    DEFAULT = 'default'
    AGENT_SOCKET = 'agent_socket'

    @classmethod
    def get_transport(self, api_config=None, env_details=None, **kwargs):
        transport = arg_or_env('transport', kwargs, self.DEFAULT)

        if transport == self.AGENT_SOCKET:
            return AgentSocket(), self.AGENT_SOCKET

        return HTTPClient(api_config, env_details), self.DEFAULT

    @classmethod
    def create_message(self, record, type, api_config, env_details):
        if type == self.AGENT_SOCKET:
            return Log(record, api_config, env_details).get_object()

        msg = LogMsg()
        msg.from_record(record)
        return msg

    @classmethod
    def create_group_message(self, messages, type, api_config, env_details):
        if type == self.AGENT_SOCKET:
            return LogGroup(messages, api_config, env_details).serialize_to_string()

        return LogMsgGroup(messages)

    @classmethod
    def get_log_url(self, type):
        if type == self.AGENT_SOCKET:
            return SOCKET_LOG_URL

        return LOG_SAVE_URL


class Transport(object):
    """
    Transport base class
    """

    def __init__(self, config=None, **kwargs):
        self.api_config = config or get_configuration(**kwargs)
        self.env_details = EnvironmentDetail(self.api_config)
        self._transport, self._transport_type = TransportTypes.get_transport(
            self.api_config,
            self.env_details,
            **kwargs
        )

    def create_message(self, record):
        return TransportTypes.create_message(
            record,
            self._transport_type,
            self.api_config,
            self.env_details,
        )

    def create_group_message(self, messages):
        return TransportTypes.create_group_message(
            messages,
            self._transport_type,
            self.api_config,
            self.env_details,
        )

    def send(self, group_message):
        self._transport.send(
            TransportTypes.get_log_url(self._transport_type),
            group_message,
        )

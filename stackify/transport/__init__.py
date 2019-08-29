import logging
import os
import sys
import urllib

from stackify.constants import DEFAULT_SOCKET_FILE
from stackify.constants import SOCKET_URL
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

PY2 = sys.version_info[0] == 2

internal_logger = logging.getLogger(__name__)


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
    def get_transport(self, api_config=None, env_details=None):
        if api_config.transport == self.AGENT_SOCKET:
            socket_url = urllib.unquote_plus(DEFAULT_SOCKET_FILE) if PY2 else urllib.parse.unquote_plus(DEFAULT_SOCKET_FILE)
            # checking if socket file exists
            if os.path.exists(socket_url):
                internal_logger.debug('Setting Agent Socket Transport.')
                api_config.transport = self.AGENT_SOCKET
                return AgentSocket()
            else:
                internal_logger.debug('Socket file not found.')

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
            return LogGroup(messages, api_config, env_details).serialize_to_string()

        return LogMsgGroup(messages)

    @classmethod
    def get_log_url(self, api_config):
        if api_config.transport == self.AGENT_SOCKET:
            return SOCKET_URL + SOCKET_LOG_URL

        return LOG_SAVE_URL


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
        self._transport.send(
            TransportTypes.get_log_url(self.api_config),
            group_message,
        )

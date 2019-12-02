from stackify.constants import LOG_SAVE_URL
from stackify.transport.base import BaseTransport
from stackify.transport.default.http import HTTPClient
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup


class DefaultTransport(BaseTransport):
    """
    Default Transport handles sending of logs directly to platform
    """
    _transport = None

    def __init__(self, api_config, env_details):
        super(DefaultTransport, self).__init__(api_config, env_details)
        self._transport = HTTPClient(api_config, env_details)

    def create_message(self, record):
        msg = LogMsg()
        msg.from_record(record)
        return msg

    def create_group_message(self, messages):
        return LogMsgGroup(messages)

    def send(self, group_message):
        self._transport.send(
            LOG_SAVE_URL,
            group_message,
        )

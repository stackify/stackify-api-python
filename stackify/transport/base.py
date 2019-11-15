from stackify.transport.agent.message import Log
from stackify.transport.agent.message import LogGroup


class BaseTransport(object):
    def __init__(self, api_config, env_details):
        self._api_config = api_config
        self._env_details = env_details

    def create_message(self, record):
        raise NotImplementedError

    def create_group_message(self, messages):
        raise NotImplementedError

    def send(self, group_message):
        raise NotImplementedError


class AgentBaseTransport(BaseTransport):
    def __init__(self, api_config, env_details):
        super(AgentBaseTransport, self).__init__(api_config, env_details)

    def create_message(self, record):
        return Log(record, self._api_config, self._env_details).get_object()

    def create_group_message(self, messages):
        return LogGroup(messages, self._api_config, self._env_details).get_object()

    def send(self, group_message):
        raise NotImplementedError

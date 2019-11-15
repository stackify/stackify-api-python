import logging

from tests.bases import ClearEnvTest
from stackify.protos import stackify_agent_pb2
from stackify.transport.base import BaseTransport
from stackify.transport.base import AgentBaseTransport
from stackify.transport.application import EnvironmentDetail
from stackify.transport.application import get_configuration

CONFIG = {
    'application': 'test_appname',
    'environment': 'test_environment',
    'api_key': 'test_apikey',
    'api_url': 'test_apiurl',
}


class BaseTransportTest(ClearEnvTest):
    def test_init(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'

        base_transport = BaseTransport(api_config, env_details)

        assert base_transport._api_config == api_config
        assert base_transport._env_details == env_details

    def test_create_message(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'
        base_transport = BaseTransport(api_config, env_details)

        self.assertRaises(NotImplementedError, base_transport.create_message, 'test_record')

    def test_create_group_message(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'
        base_transport = BaseTransport(api_config, env_details)

        self.assertRaises(NotImplementedError, base_transport.create_group_message, 'test_messages')

    def test_send(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'
        base_transport = BaseTransport(api_config, env_details)

        self.assertRaises(NotImplementedError, base_transport.send, 'test_group_message')


class AgentBaseTransportTest(ClearEnvTest):
    def test_init(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'

        agent_base_transport = AgentBaseTransport(api_config, env_details)

        assert agent_base_transport._api_config == api_config
        assert agent_base_transport._env_details == env_details

    def test_create_message(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'
        agent_base_transport = AgentBaseTransport(api_config, env_details)

        message = agent_base_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_create_group_message(self):
        api_config = get_configuration(**CONFIG)
        env_details = EnvironmentDetail(api_config)
        agent_base_transport = AgentBaseTransport(api_config, env_details)

        message = agent_base_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = agent_base_transport.create_group_message([message])

        assert isinstance(group_message, stackify_agent_pb2.LogGroup)

    def test_send(self):
        api_config = 'test_api_config'
        env_details = 'test_env_details'
        agent_base_transport = AgentBaseTransport(api_config, env_details)

        self.assertRaises(NotImplementedError, agent_base_transport.send, 'test_group_message')

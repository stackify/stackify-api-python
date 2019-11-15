import logging
from unittest import TestCase
from mock import patch

from stackify.protos import stackify_agent_pb2
from stackify.transport import application
from stackify.transport.agent import AgentHTTPTransport
from stackify.transport.agent import AgentSocketTransport


class AgentSocketTransportTest(TestCase):
    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)
        self.agent_socket_transport = AgentSocketTransport(self.config, self.env_details)

    def test_init(self):
        assert self.agent_socket_transport._api_config == self.config
        assert self.agent_socket_transport._env_details == self.env_details

    def test_create_message(self):
        message = self.agent_socket_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_create_group_message(self):
        message = self.agent_socket_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        group_message = self.agent_socket_transport.create_group_message([message])

        assert isinstance(group_message, stackify_agent_pb2.LogGroup)

    @patch('requests_unixsocket.Session.post')
    def test_send(self, mock_post):
        message = self.agent_socket_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = self.agent_socket_transport.create_group_message([message])

        self.agent_socket_transport.send(group_message)

        assert mock_post.called
        assert mock_post.call_args_list[0][0][0] == 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock/log'
        assert mock_post.call_args_list[0][1]['headers']['Content-Type'] == 'application/x-protobuf'


class AgentHTTPTransportTest(TestCase):

    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)
        self.agent_http_transport = AgentHTTPTransport(self.config, self.env_details)

    def test_init(self):
        assert self.agent_http_transport._api_config == self.config
        assert self.agent_http_transport._env_details == self.env_details

    def test_create_message(self):
        message = self.agent_http_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_create_group_message(self):
        message = self.agent_http_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        group_message = self.agent_http_transport.create_group_message([message])

        assert isinstance(group_message, stackify_agent_pb2.LogGroup)

    @patch('requests.post')
    def test_send(self, mock_post):
        message = self.agent_http_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = self.agent_http_transport.create_group_message([message])

        self.agent_http_transport.send(group_message)

        assert mock_post.called
        assert mock_post.call_args_list[0][0][0] == 'https://localhost:10601/log'
        assert mock_post.call_args_list[0][1]['headers']['Content-Type'] == 'application/x-protobuf'

import logging
from mock import patch

from tests.bases import ClearEnvTest
from stackify.protos import stackify_agent_pb2
from stackify.transport import Transport
from stackify.transport.agent import AgentSocket
from stackify.transport.default import HTTPClient
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup


class TestTransport(ClearEnvTest):
    def test_invalid_transport(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'transport': 'invalid',
        }

        transport = Transport(**config)

        assert isinstance(transport._transport, HTTPClient)

    def test_default_transport(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = Transport(**config)

        assert isinstance(transport._transport, HTTPClient)

    def test_default_create_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message'}))

        assert isinstance(message, LogMsg)

    def test_default_create_group_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message'}))
        group_message = transport.create_group_message([message])

        assert isinstance(group_message, LogMsgGroup)

    @patch('stackify.transport.default.http.HTTPClient.send')
    def test_default_send_url(self, mock_send):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == '/Log/Save'

    def test_agent_socket_transport(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = Transport(**config)

        assert isinstance(transport._transport, AgentSocket)

    def test_agent_socket_create_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_agent_socket_create_group_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])

        assert isinstance(group_message, stackify_agent_pb2.LogGroup)

    @patch('stackify.transport.agent.agent_socket.AgentSocket.send')
    def test_agent_socket_send_url(self, mock_send):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == 'test_socketurl/log'

    @patch('stackify.transport.agent.agent_socket.AgentSocket.send')
    def test_agent_socket_send_url_default(self, mock_send):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'transport': 'agent_socket',
        }

        transport = Transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock/log'

import logging
from mock import patch

from tests.bases import ClearEnvTest
from stackify.constants import AGENT_LOG_URL
from stackify.constants import DEFAULT_HTTP_ENDPOINT
from stackify.protos import stackify_agent_pb2
from stackify.transport import configure_transport
from stackify.transport.agent import AgentHTTPTransport
from stackify.transport.agent import AgentSocketTransport
from stackify.transport.default import DefaultTransport
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

        transport = configure_transport(**config)

        assert isinstance(transport, DefaultTransport)

    def test_default_transport(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = configure_transport(**config)

        assert isinstance(transport, DefaultTransport)

    def test_default_create_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = configure_transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message'}))

        assert isinstance(message, LogMsg)

    def test_default_create_group_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
        }

        transport = configure_transport(**config)
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

        transport = configure_transport(**config)
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

        transport = configure_transport(**config)

        assert isinstance(transport, AgentSocketTransport)

    def test_agent_socket_create_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = configure_transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_agent_socket_create_group_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'socket_url': 'test_socketurl',
            'transport': 'agent_socket',
        }

        transport = configure_transport(**config)
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

        transport = configure_transport(**config)
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

        transport = configure_transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock/log'

    def test_agent_http_transport(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'http_endpoint': 'test.url',
            'transport': 'agent_http',
        }

        transport = configure_transport(**config)

        assert isinstance(transport, AgentHTTPTransport)

    def test_agent_http_create_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'http_endpoint': 'test.url',
            'transport': 'agent_http',
        }

        transport = configure_transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, stackify_agent_pb2.LogGroup.Log)

    def test_agent_http_create_group_message(self):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'http_endpoint': 'test.url',
            'transport': 'agent_http',
        }

        transport = configure_transport(**config)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])

        assert isinstance(group_message, stackify_agent_pb2.LogGroup)

    @patch('stackify.transport.agent.agent_http.AgentHTTP.send')
    def test_agent_http_send_url(self, mock_send):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'http_endpoint': 'test.url',
            'transport': 'agent_http',
        }

        transport = configure_transport(**config)
        assert isinstance(transport, AgentHTTPTransport)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == 'test.url/log'

    @patch('stackify.transport.agent.agent_http.AgentHTTP.send')
    def test_agent_http_send_url_default(self, mock_send):
        config = {
            'application': 'test_appname',
            'environment': 'test_environment',
            'api_key': 'test_apikey',
            'api_url': 'test_apiurl',
            'transport': 'agent_http',
        }

        transport = configure_transport(**config)
        assert isinstance(transport, AgentHTTPTransport)
        message = transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = transport.create_group_message([message])
        transport.send(group_message)

        assert mock_send.called
        assert mock_send.call_args_list[0][0][0] == DEFAULT_HTTP_ENDPOINT + AGENT_LOG_URL

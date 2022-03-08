import imp
import retrying
from unittest import TestCase
from mock import patch
import os

import stackify
from tests.bases import fake_retry_decorator


class TestAgentSocket(TestCase):

    @classmethod
    def setUpClass(self):
        retrying.retry = fake_retry_decorator(3)
        imp.reload(stackify.transport.agent.agent_socket)

    @classmethod
    def tearDownClass(self):
        imp.reload(retrying)
        imp.reload(stackify.transport.agent.agent_socket)

    def setUp(self):
        self.agent_socket = stackify.transport.agent.agent_socket.AgentSocket()

    @patch('requests_unixsocket.Session.post')
    def test_send(self, mock_post):
        url = 'http+unix://test_url'
        message = 'message'

        self.agent_socket.send(url, message)

        assert mock_post.called
        assert mock_post.call_args_list[0][0][0] == 'http+unix://test_url'

    @patch('requests_unixsocket.Session.post')
    def test_send_should_use_defaut_socket(self, mock_post):
        url = '/test_url'
        message = 'message'

        self.agent_socket.send(url, message)

        assert mock_post.called
        if os.name == 'nt':
            assert mock_post.call_args_list[0][0][0] == 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock\\test_url'
        else:
            assert mock_post.call_args_list[0][0][0] == 'http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock/test_url'

    @patch('requests_unixsocket.Session.post')
    def test_send_should_include_headers(self, mock_post):
        url = '/test_url'
        message = 'message'

        self.agent_socket.send(url, message)

        assert mock_post.called
        assert mock_post.call_args_list[0][1]['headers']['Content-Type'] == 'application/x-protobuf'

    @patch('requests_unixsocket.Session.post')
    def test_retry(self, mock_post):
        url = '/test_url'
        message = 'message'
        mock_post.side_effect = Exception('some error')

        with self.assertRaises(Exception):
            self.agent_socket.send(url, message)

        assert mock_post.call_count == 3

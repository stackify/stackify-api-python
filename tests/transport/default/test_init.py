import logging
from unittest import TestCase
from mock import patch

from stackify.transport import application
from stackify.transport.default import DefaultSocketTransport
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup


class AgentSocketTransportTest(TestCase):
    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)
        self.default_transport = DefaultSocketTransport(self.config, self.env_details)

    def test_init(self):
        assert self.default_transport._api_config == self.config
        assert self.default_transport._env_details == self.env_details

    def test_create_message(self):
        message = self.default_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        assert isinstance(message, LogMsg)

    def test_create_group_message(self):
        message = self.default_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))

        group_message = self.default_transport.create_group_message([message])

        assert isinstance(group_message, LogMsgGroup)

    @patch('requests.post')
    def test_send(self, mock_post):
        message = self.default_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = self.default_transport.create_group_message([message])

        self.default_transport.send(group_message)

        assert mock_post.called
        assert mock_post.call_args_list[0][0][0] == 'test_apiurl/Metrics/IdentifyApp'
        assert mock_post.call_args_list[0][1]['headers']['Content-Type'] == 'application/json'

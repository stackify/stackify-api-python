import gzip
import json
import logging
from unittest import TestCase
from mock import patch
from requests.models import Response

try:
    from cStringIO import StringIO
except Exception:
    try:
        from StringIO import StringIO
    except Exception:
        pass  # python 3, we use a new function in gzip

from stackify.transport import application
from stackify.transport.default import DefaultTransport
from stackify.transport.default.log import LogMsg
from stackify.transport.default.log import LogMsgGroup


def parse_gzip_data(data):
    if hasattr(gzip, 'decompress'):
        return gzip.decompress(data).decode("utf-8")
    else:
        sio = StringIO()
        sio.write(data)
        sio.seek(0)
        g = gzip.GzipFile(fileobj=sio, mode='rb')
        transaction = g.read()
        g.close()
        return transaction.decode("utf-8")


class AgentSocketTransportTest(TestCase):
    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)
        self.default_transport = DefaultTransport(self.config, self.env_details)

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
        res = Response()
        res._content = json.dumps({
            'DeviceID': None,
            'DeviceAppID': None,
            'AppNameID': 'test',
            'EnvID': 0,
            'Env': 'test_environment',
            'AppName': 'test_appname',
            'AppEnvID': 'test',
            'DeviceAlias': 'test'
        })
        mock_post.side_effect = [res, Response()]
        message = self.default_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = self.default_transport.create_group_message([message])

        self.default_transport.send(group_message)

        assert mock_post.called
        assert mock_post.call_count == 2
        assert mock_post.call_args_list[0][0][0] == 'test_apiurl/Metrics/IdentifyApp'
        assert mock_post.call_args_list[0][1]['headers']['Content-Type'] == 'application/json'
        assert mock_post.call_args_list[1][0][0] == 'test_apiurl/Log/Save'
        assert mock_post.call_args_list[1][1]['headers']['Content-Type'] == 'application/json'

    @patch('requests.post')
    def test_json_data(self, mock_post):
        res = Response()
        res._content = json.dumps({
            'DeviceID': None,
            'DeviceAppID': None,
            'AppNameID': 'test',
            'EnvID': 0,
            'Env': 'test_environment',
            'AppName': 'test_appname',
            'AppEnvID': 'test',
            'DeviceAlias': 'test'
        })
        mock_post.side_effect = [res, Response()]
        message = self.default_transport.create_message(logging.makeLogRecord({'mgs': 'message', 'funcName': 'foo'}))
        group_message = self.default_transport.create_group_message([message])

        self.default_transport.send(group_message)

        assert mock_post.called
        assert mock_post.call_count == 2
        assert mock_post.call_args_list[1][0][0] == 'test_apiurl/Log/Save'

        payload = json.loads(parse_gzip_data(mock_post.call_args_list[1][1]['data']))
        assert payload.get('AppName') == 'test_appname'
        assert payload.get('Env') == 'test_environment'
        assert payload.get('ServerName')
        assert payload.get('AppNameID') == 'test'
        assert payload.get('Logger')
        assert payload.get('Msgs')

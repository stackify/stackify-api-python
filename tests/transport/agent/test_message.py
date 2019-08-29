import logging
from unittest import TestCase

from stackify.protos import stackify_agent_pb2
from stackify.transport import application
from stackify.transport.agent.message import Log
from stackify.transport.agent.message import LogGroup


class TestLog(TestCase):
    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)

    def test_get_object(self):
        with self.assertLogs('foo', level='INFO') as logging_watcher:
            logging.getLogger('foo').info('some log')

            log = Log(logging_watcher.records[0], self.config, self.env_details).get_object()

            assert isinstance(log, stackify_agent_pb2.LogGroup.Log)

    def test_info_log_details(self):
        with self.assertLogs('foo', level='INFO') as logging_watcher:
            logging.getLogger('foo').info('some log')

            log = Log(logging_watcher.records[0], self.config, self.env_details).get_object()

            assert log.message == 'some log'
            assert log.level == 'INFO'
            assert log.thread_name
            assert log.date_millis
            assert log.source_method
            assert log.source_line
            assert not log.HasField('error')

    def test_info_error_details(self):
        with self.assertLogs('foo', level='ERROR') as logging_watcher:
            logging.getLogger('foo').error('some error')

            log = Log(logging_watcher.records[0], self.config, self.env_details).get_object()

            assert log.message == 'some error'
            assert log.level == 'ERROR'
            assert log.thread_name
            assert log.date_millis
            assert log.source_method
            assert log.source_line
            assert not log.HasField('error')

    def test_info_exception_details(self):
        with self.assertLogs('foo', level='ERROR') as logging_watcher:
            try:
                1 / 0
            except Exception:
                logging.getLogger('foo').exception('some error')

            log = Log(logging_watcher.records[0], self.config, self.env_details).get_object()

            assert log.message == 'some error'
            assert log.level == 'ERROR'
            assert log.thread_name
            assert log.date_millis
            assert log.source_method
            assert log.source_line
            assert log.HasField('error')

            error = log.error
            assert error.date_millis
            assert error.HasField('environment_detail')
            assert error.HasField('error_item')

            environment_detail = error.environment_detail
            assert environment_detail.application_name == 'test_appname'
            assert environment_detail.configured_application_name == 'test_appname'
            assert environment_detail.configured_environment_name == 'test_environment'
            assert environment_detail.device_name == self.env_details.deviceName
            assert environment_detail.application_location == self.env_details.appLocation

            error_item = error.error_item
            assert error_item.message == 'division by zero'
            assert error_item.error_type == 'ZeroDivisionError'
            assert error_item.source_method == 'test_info_exception_details'
            assert len(error_item.stacktrace)

            stacktraces = error_item.stacktrace
            for stacktrace in stacktraces:
                assert stacktrace.code_filename.endswith('test_message.py')
                assert stacktrace.method == 'test_info_exception_details'
                assert stacktrace.line_number


class TestLogGroup(TestCase):
    def setUp(self):
        self.config = application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        self.env_details = application.EnvironmentDetail(self.config)

    def test_get_object(self):
        log_group = LogGroup([], self.config, self.env_details).get_object()

        assert isinstance(log_group, stackify_agent_pb2.LogGroup)

    def test_details(self):
        with self.assertLogs('foo', level='INFO') as logging_watcher:
            logging.getLogger('foo').info('some log')

            log = Log(logging_watcher.records[0], self.config, self.env_details).get_object()
            log_group = LogGroup([log], self.config, self.env_details).get_object()

            assert log_group.environment == 'test_environment'
            assert log_group.application_name == 'test_appname'
            assert log_group.server_name == self.env_details.deviceName
            assert log_group.application_location == self.env_details.appLocation
            assert log_group.logger
            assert log_group.platform == 'python'
            assert len(log_group.logs)

            log_group_logs = log_group.logs
            assert log_group_logs[0].message == 'some log'
            assert log_group_logs[0].level == 'INFO'
            assert log_group_logs[0].thread_name
            assert log_group_logs[0].date_millis
            assert log_group_logs[0].source_method
            assert log_group_logs[0].source_line
            assert not log_group_logs[0].HasField('error')

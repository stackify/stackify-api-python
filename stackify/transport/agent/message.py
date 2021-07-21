import sys
import traceback

from stackify.constants import RECORD_VARS
from stackify.protos import stackify_agent_pb2
from stackify.utils import data_to_json


class BaseMessage(object):
    """
    Base Class wrapper for protobuf classes
    This will help to create protobuf object with ease
    """
    obj = None

    def get_object(self):
        # return protobuf object
        return self.obj


class EnvironmentDetail(BaseMessage):
    """
    Class wrapper for protobuf LogGroup.Log.Error.EnvironmentDetail class
    """

    def __init__(self, api_config, environment_details):
        self.obj = env_details = stackify_agent_pb2.LogGroup.Log.Error.EnvironmentDetail()
        env_details.application_name = api_config.application
        env_details.configured_application_name = api_config.application
        env_details.configured_environment_name = api_config.environment
        env_details.device_name = environment_details.deviceName
        env_details.application_location = environment_details.appLocation


class TraceFrame(BaseMessage):
    """
    Class wrapper for protobuf LogGroup.Log.Error.ErrorItem.TraceFrame class
    """

    def __init__(self, filename, lineno, method):
        self.obj = trace_frame = stackify_agent_pb2.LogGroup.Log.Error.ErrorItem.TraceFrame()
        trace_frame.code_filename = filename
        trace_frame.line_number = lineno
        trace_frame.method = method


class ErrorItem(BaseMessage):
    """
    Class wrapper for protobuf LogGroup.Log.Error.ErrorItem.TraceFrame class
    """

    def __init__(self, exc_info):
        self.obj = error_item = stackify_agent_pb2.LogGroup.Log.Error.ErrorItem()

        if not exc_info:
            type_, value, tb = sys.exc_info()
        else:
            type_, value, tb = exc_info

        stacks = traceback.extract_tb(tb)

        error_item.message = str(value)
        error_item.error_type = type_.__name__
        error_item.source_method = stacks[-1][2]

        for filename, lineno, method, text in reversed(stacks):
            error_item.stacktrace.append(TraceFrame(filename, lineno, method).get_object())


class Error(BaseMessage):
    """
    Class wrapper for protobuf LogGroup.Log.Error class
    """

    def __init__(self, record, api_config, env_details):
        self.obj = error = stackify_agent_pb2.LogGroup.Log.Error()
        error.date_millis = int(record.created * 1000)
        error.error_item.MergeFrom(ErrorItem(record.exc_info).get_object())
        error.environment_detail.MergeFrom(EnvironmentDetail(api_config, env_details).get_object())


class Log(BaseMessage):
    """
    Class wrapper for protobuf LogGroup.Log class
    """

    def __init__(self, record, api_config, env_details):
        self.obj = log = stackify_agent_pb2.LogGroup.Log()
        log.message = record.getMessage()
        log.thread_name = record.threadName or record.thread
        log.date_millis = int(record.created * 1000)
        log.level = record.levelname
        log.source_method = record.funcName
        log.source_line = record.lineno

        if hasattr(record, 'log_id'):
            log.id = record.log_id

        if hasattr(record, 'trans_id'):
            log.transaction_id = record.trans_id

        data = {k: v for k, v in record.__dict__.items()
                if k not in RECORD_VARS}

        if data:
            log.data = data_to_json(data)

        if record.exc_info:
            log.error.MergeFrom(Error(record, api_config, env_details).get_object())


class LogGroup(BaseMessage):
    """
    Class wrapper for protobuf LogGroup class
    """

    def __init__(self, messages, api_config, env_details, logger=None):
        self.obj = log_group = stackify_agent_pb2.LogGroup()
        log_group.environment = api_config.environment
        log_group.application_name = api_config.application
        log_group.server_name = env_details.deviceName
        log_group.application_location = env_details.appLocation
        log_group.logger = logger or __name__
        log_group.platform = 'python'
        log_group.logs.extend(messages)

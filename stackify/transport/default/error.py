import traceback
import sys

from stackify.transport.default.formats import JSONObject


class ErrorItem(JSONObject):
    def __init__(self):
        self.Message = None  # exception message
        self.ErrorType = None  # exception class name
        self.ErrorTypeCode = None
        self.Data = None  # custom data
        self.SourceMethod = None
        self.StackTrace = []  # array of TraceFrames
        self.InnerError = None  # cause?

    def load_stack(self, exc_info=None):
        if not exc_info:
            type_, value, tb = sys.exc_info()
        else:
            type_, value, tb = exc_info

        stacks = traceback.extract_tb(tb)

        self.ErrorType = type_.__name__
        self.Message = str(value)
        self.SourceMethod = stacks[-1][2]
        for filename, lineno, method, text in reversed(stacks):
            self.StackTrace.append(TraceFrame(filename, lineno, method))


class TraceFrame(JSONObject):
    def __init__(self, filename, lineno, method):
        self.CodeFileName = filename
        self.LineNum = lineno
        self.Method = method


class StackifyError(JSONObject):
    def __init__(self):
        self.EnvironmentDetail = None  # environment detail object
        self.OccurredEpochMillis = None
        self.Error = None  # ErrorItem object
        self.CustomerName = None
        self.UserName = None

    def load_exception(self, exc_info=None):
        self.Error = ErrorItem()
        self.Error.load_stack(exc_info)

    def from_record(self, record):
        self.load_exception(record.exc_info)
        self.OccurredEpochMillis = int(record.created * 1000)

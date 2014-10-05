import json
import logging

from stackify.formats import JSONObject

from stackify import MAX_BATCH, LOGGING_LEVELS
from stackify.error import StackifyError


# this is used to separate builtin keys from user-specified keys
RECORD_VARS = set(logging.LogRecord('','','','','','','','').__dict__.keys())


class LogMsg(JSONObject):
    def __init__(self):
        self.Msg = None
        self.data = None
        self.Ex = None # a StackifyError object
        #self.Th = threading.current_thread().ident
        self.Th = None
        self.EpochMs = None
        self.Level = None
        self.TransID = None
        # filename, line_number, function = internal_log.findCaller()
        self.SrcMethod = None
        self.SrcLine = None

    def from_record(self, record):
        self.Msg = record.getMessage()
        self.Th = record.threadName or record.thread
        self.EpochMs = int(record.created * 1000)
        self.Level = record.levelname
        self.SrcMethod = record.funcName
        self.SrcLine = record.lineno

        # check for user-specified keys
        data = { k:v for k,v in record.__dict__.items() if k not in RECORD_VARS }

        if data:
            self.data = json.dumps(data, default=lambda x: x.__dict__)

        if record.exc_info:
            self.Ex = StackifyError()
            self.Ex.from_record(record)


class LogMsgGroup(JSONObject):
    def __init__(self, msgs, logger=None):
        self.Logger = logger or __name__
        self.Msgs = msgs
        self.CDID = None
        self.CDAppID = None
        self.AppNameID = None
        self.ServerName = None


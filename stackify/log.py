import json
import logging

from stackify.formats import JSONObject
from stackify.error import StackifyError


# this is used to separate builtin keys from user-specified keys
RECORD_VARS = set(logging.LogRecord('', '', '', '', '', '', '', '').__dict__.keys())

# the "message" attribute is saved on the record object by a Formatter
RECORD_VARS.add('message')
RECORD_VARS.add('trans_id')
RECORD_VARS.add('log_id')


class LogMsg(JSONObject):
    def __init__(self):
        self.ID = None
        self.Msg = None
        self.data = None
        self.Ex = None  # a StackifyError object
        self.Th = None
        self.EpochMs = None
        self.Level = None
        self.TransID = None
        self.SrcMethod = None
        self.SrcLine = None

    def from_record(self, record):
        self.ID = hasattr(record, 'log_id') and record.log_id or None
        self.Msg = record.getMessage()
        self.Th = record.threadName or record.thread
        self.EpochMs = int(record.created * 1000)
        self.Level = record.levelname
        self.TransID = hasattr(record, 'trans_id') and record.trans_id or None
        self.SrcMethod = record.funcName
        self.SrcLine = record.lineno

        # check for user-specified keys
        data = {k: v for k, v in record.__dict__.items()
                if k not in RECORD_VARS}

        if data:
            self.data = json.dumps(data, default=lambda x: hasattr(x, '__dict__') and x.__dict__ or x.__str__())

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

from stackify.constants import RECORD_VARS
from stackify.transport.default.formats import JSONObject
from stackify.transport.default.error import StackifyError
from stackify.utils import data_to_json
from stackify.utils import extract_request


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

        data = extract_request(data)

        if data:
            self.data = data_to_json(data)

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

import time
import threading
import logging
import json

from stackify.application import JSONObject


MAX_BATCH = 100


LOGGING_LEVELS = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET'
}


class LogMsg(JSONObject):
    def __init__(self, message, data=None):
        self.Msg = message
        self.data = json.dumps(data, default=lambda x: x.__dict__) if data else None
        self.Ex = None # a StackifyError object
        self.Th = threading.current_thread().ident
        self.EpochMs = int(time.time() * 1000)
        self.Level = None
        self.TransID = None
        # filename, line_number, function = internal_log.findCaller()
        self.SrcMethod = None
        self.SrcLine = None


class LogMsgGroup(JSONObject):
    def __init__(self, msgs, logger=None):
        self.Logger = logger or __name__
        self.Msgs = msgs
        self.CDID = None
        self.CDAppID = None
        self.AppNameID = None
        self.ServerName = None

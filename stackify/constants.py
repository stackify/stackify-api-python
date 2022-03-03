import logging


API_URL = 'https://api.stackify.com'
IDENTIFY_URL = '/Metrics/IdentifyApp'
LOG_SAVE_URL = '/Log/Save'

# using `%2F` instead of `/` as per package documentation
DEFAULT_SOCKET_FILE = '%2Fusr%2Flocal%2Fstackify%2Fstackify.sock'
DEFAULT_HTTP_ENDPOINT = 'https://localhost:10601'
SOCKET_URL = 'http+unix://' + DEFAULT_SOCKET_FILE
AGENT_LOG_URL = '/log'

API_REQUEST_INTERVAL_IN_SEC = 30

MAX_BATCH = 100
QUEUE_SIZE = 1000
READ_TIMEOUT = 5000

LOGGING_LEVELS = {
    logging.CRITICAL: 'CRITICAL',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG',
    logging.NOTSET: 'NOTSET'
}
DEFAULT_LEVEL = logging.INFO

# this is used to separate builtin keys from user-specified keys
RECORD_VARS = set(logging.LogRecord('', '', '', '', '', '', '', '').__dict__.keys())

# the "message" attribute is saved on the record object by a Formatter
RECORD_VARS.add('message')
RECORD_VARS.add('trans_id')
RECORD_VARS.add('log_id')

TRANSPORT_TYPE_DEFAULT = 'default'
TRANSPORT_TYPE_AGENT_SOCKET = 'agent_socket'
TRANSPORT_TYPE_AGENT_HTTP = 'agent_http'

DEFAULT_RUM_SCRIPT_URL = "https://stckjs.stackify.com/stckjs.js"
DEFAULT_RUM_KEY = ""

import logging


API_URL = 'https://api.stackify.com'
IDENTIFY_URL = '/Metrics/IdentifyApp'
LOG_SAVE_URL = '/Log/Save'
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

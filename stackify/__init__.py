"""
Stackify Python API
"""

__version__ = '0.0.1'


API_URL = 'https://api.stackify.com'

READ_TIMEOUT = 5000


import logging

logging.basicConfig()

from stackify.application import ApiConfiguration
from stackify.http import HTTPClient


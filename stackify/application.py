import socket
import os

from stackify import API_URL
from stackify.formats import JSONObject


class EnvironmentDetail(JSONObject):
    def __init__(self, api_config):
        self.deviceName = socket.gethostname()
        self.appLocation = os.getcwd()
        self.configuredAppName = api_config.application
        self.configuredEnvironmentName = api_config.environment


class ApiConfiguration:
    def __init__(self, api_key, application, environment, api_url=API_URL):
        self.api_key = api_key
        self.api_url = api_url
        self.application = application
        self.environment = environment


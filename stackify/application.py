import socket
import os
import json

from stackify import API_URL


class JSONObject(object):
    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__)


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


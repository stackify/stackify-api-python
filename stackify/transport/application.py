import socket
import os

from stackify.utils import arg_or_env
from stackify.constants import API_URL
from stackify.constants import SOCKET_URL
from stackify.transport.default.formats import JSONObject


class EnvironmentDetail(JSONObject):
    def __init__(self, api_config):
        self.deviceName = socket.gethostname()
        self.appLocation = os.getcwd()
        self.configuredAppName = api_config.application
        self.configuredEnvironmentName = api_config.environment


class ApiConfiguration:
    def __init__(self, api_key, application, environment, api_url=API_URL, socket_url=SOCKET_URL, transport=None):
        self.api_key = api_key
        self.api_url = api_url
        self.application = application
        self.environment = environment
        self.socket_url = socket_url
        self.transport = transport


def get_configuration(**kwargs):
    return ApiConfiguration(
        application=arg_or_env('application', kwargs),
        environment=arg_or_env('environment', kwargs),
        api_key=arg_or_env('api_key', kwargs),
        api_url=arg_or_env('api_url', kwargs, API_URL),
        socket_url=arg_or_env('socket_url', kwargs, SOCKET_URL),
        transport=arg_or_env('transport', kwargs, 'default'),
    )

import socket
import os

from stackify.constants import API_URL
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


def arg_or_env(name, args, default=None):
    env_name = 'STACKIFY_{0}'.format(name.upper())
    try:
        value = args.get(name)
        if not value:
            value = os.environ[env_name]
        return value
    except KeyError:
        if default:
            return default
        else:
            raise NameError('You must specify the keyword argument {0} or environment variable {1}'.format(name, env_name))


def get_configuration(**kwargs):
    return ApiConfiguration(
        application=arg_or_env('application', kwargs),
        environment=arg_or_env('environment', kwargs),
        api_key=arg_or_env('api_key', kwargs),
        api_url=arg_or_env('api_url', kwargs, API_URL))

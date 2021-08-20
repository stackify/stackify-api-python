import socket
import os
import logging

from stackify.utils import arg_or_env
from stackify.constants import API_URL
from stackify.constants import DEFAULT_HTTP_ENDPOINT
from stackify.constants import SOCKET_URL
from stackify.constants import TRANSPORT_TYPE_AGENT_HTTP
from stackify.constants import TRANSPORT_TYPE_AGENT_SOCKET
from stackify.constants import TRANSPORT_TYPE_DEFAULT
from stackify.transport.default.formats import JSONObject
from stackify.constants import DEFAULT_RUM_SCRIPT_URL
from stackify.constants import DEFAULT_RUM_KEY
from stackify.utils import RegexValidator, ConfigError
from stackify import config

internal_logger = logging.getLogger(__name__)


class EnvironmentDetail(JSONObject):
    """
    EnvironmentDetail class that stores application environment
    and user define details
    """

    def __init__(self, api_config):
        self.deviceName = socket.gethostname()
        self.appLocation = os.getcwd()
        self.configuredAppName = api_config.application
        self.configuredEnvironmentName = api_config.environment


class ApiConfiguration:
    """
    ApiConfiguration class that stores application configurations
    """

    def __init__(
        self,
        api_key,
        application,
        environment,
        api_url=API_URL,
        socket_url=SOCKET_URL,
        transport=None,
        http_endpoint=DEFAULT_HTTP_ENDPOINT,
        rum_script_url=DEFAULT_RUM_SCRIPT_URL,
        rum_key=DEFAULT_RUM_KEY
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.application = application
        self.environment = environment
        self.socket_url = socket_url
        self.http_endpoint = http_endpoint
        self.transport = transport

        self.rum_script_url = DEFAULT_RUM_SCRIPT_URL
        self.rum_key = DEFAULT_RUM_KEY

        # Rum config validation
        if rum_script_url != DEFAULT_RUM_SCRIPT_URL:
            self.validate(
                RegexValidator("^((((https?|ftps?|gopher|telnet|nntp)://)|(mailto:|news:))(%[0-9A-Fa-f]{2}|[-\(\)_.!~*';/?:@&=+$,A-Za-z0-9])+)([).!';/?:,][\[:blank:|:blank:\]])?$"),
                rum_script_url,
                'rum_script_url'
            )
            config.rum_script_url = self.rum_script_url

        if rum_key != DEFAULT_RUM_KEY:
            self.validate(
                RegexValidator("^[A-Za-z0-9_-]+$"),
                rum_key,
                'rum_key'
            )
            config.rum_key = self.rum_key

        config.environment = self.environment
        config.application = self.application

    def validate(self, validator, value, key):
        if not validator:
            return

        try:
            value = validator(value, key)
            setattr(self, key, str(value))
        except ConfigError as e:
            internal_logger.exception(str(e))


def get_configuration(**kwargs):
    """
    return application configuration depending on users input,
    application environment and application config
    """

    transport = arg_or_env('transport', kwargs, TRANSPORT_TYPE_DEFAULT)

    if transport in [TRANSPORT_TYPE_AGENT_SOCKET, TRANSPORT_TYPE_AGENT_HTTP]:
        api_key = arg_or_env('api_key', kwargs, '')
    else:
        api_key = arg_or_env('api_key', kwargs)

    return ApiConfiguration(
        application=arg_or_env('application', kwargs),
        environment=arg_or_env('environment', kwargs),
        api_key=api_key,
        api_url=arg_or_env('api_url', kwargs, API_URL),
        socket_url=arg_or_env('socket_url', kwargs, SOCKET_URL),
        http_endpoint=arg_or_env('http_endpoint', kwargs, DEFAULT_HTTP_ENDPOINT, env_key='STACKIFY_TRANSPORT_HTTP_ENDPOINT'),
        transport=transport,
        rum_script_url=arg_or_env('rum_script_url', kwargs, DEFAULT_RUM_SCRIPT_URL, env_key='RETRACE_RUM_SCRIPT_URL'),
        rum_key=arg_or_env('rum_key', kwargs, DEFAULT_RUM_KEY, env_key='RETRACE_RUM_KEY')
    )

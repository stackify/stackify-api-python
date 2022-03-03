import os
import json
import logging

internal_logger = logging.getLogger(__name__)


def arg_or_env(name, args, default=None, env_key=None):
    env_name = env_key or 'STACKIFY_{0}'.format(name.upper())
    try:
        value = args.get(name)
        if not value:
            value = os.environ[env_name]
        return value
    except KeyError:
        if default is not None:
            return default
        else:
            raise NameError('You must specify the keyword argument {0} or environment variable {1}'.format(name, env_name))


def data_to_json(data):
    try:
        return json.dumps(data, default=lambda x: get_default_object(x))
    except Exception as e:
        internal_logger.exception('Failed to serialize object to json: {} - Exception: {}'.format(str(data), str(e)))
        return str(data)  # String representation of the object


def extract_request(data):
    if 'request' in data and "WSGIRequest" in str(data['request']):
        new_request = {}
        obj = data['request']

        if hasattr(obj, 'path'):
            new_request['path'] = obj.path

        if hasattr(obj, 'method'):
            new_request['method'] = obj.method

        if hasattr(obj, 'POST'):
            new_request['form'] = obj.POST

        if hasattr(obj, 'GET'):
            new_request['query'] = obj.GET

        if hasattr(obj, 'content_type'):
            new_request['content_type'] = obj.content_type

        data['request'] = new_request

    return data


def get_default_object(obj):
    if object_is_iterable(obj):
        return [item for item in obj]

    return hasattr(obj, '__dict__') and obj.__dict__ or obj.__str__()


def object_is_iterable(obj):
    return hasattr(obj, '__iter__') or isinstance(obj, str)
